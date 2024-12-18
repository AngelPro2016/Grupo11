from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from datetime import timedelta

from .choices import CATEGORIAS
from .validadores import (
    validar_cedula,
    validar_telefono,
    validacion_especial,
)

# Configuración de IVA
IVA_PERCENT = getattr(settings, 'IVA_PERCENT', Decimal("0.15"))


# Modelo Clientes
class Clientes(models.Model):
    cedula = models.CharField(
        primary_key=True, max_length=10, unique=True, validators=[validar_cedula]
    )
    nombre = models.CharField(max_length=50, blank=False, verbose_name="Nombre del cliente:", validators=[validacion_especial])
    apellido = models.CharField(max_length=50, blank=False)
    telefono = models.CharField(max_length=10, validators=[validar_telefono])
    email = models.EmailField(unique=True)
    direccion = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_nacimiento = models.DateField()

    def clean(self):
        edad_minima = self.fecha_nacimiento + relativedelta(years=18)
        if edad_minima > timezone.now().date():
            raise ValidationError("El cliente debe ser mayor de 18 años.")

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        db_table = "ventas_clientes"


# Modelo Productos
class Productos(models.Model):
    codigo = models.CharField(primary_key=True, max_length=10, unique=True)
    nombre = models.CharField(max_length=50, blank=False, verbose_name="Nombre del producto:", validators=[validacion_especial])
    marca = models.CharField(max_length=50, unique=True, validators=[validacion_especial])
    categoria = models.CharField(max_length=100, choices=CATEGORIAS)
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio del producto:")
    cantidad_stock = models.IntegerField(verbose_name="Cantidad en stock:")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_elaboracion = models.DateField()
    fecha_vencimiento = models.DateField()

    def clean(self):
        if self.fecha_vencimiento <= self.fecha_elaboracion:
            raise ValidationError("La fecha de vencimiento debe ser posterior a la fecha de elaboración.")
        
        max_diferencia = timedelta(days=5 * 365)  # 5 años
        if self.fecha_vencimiento - self.fecha_elaboracion > max_diferencia:
            raise ValidationError("La fecha de vencimiento no puede superar los 5 años después de la fecha de elaboración.")

    def actualizar_stock(self, cantidad):
        if cantidad > self.cantidad_stock:
            raise ValueError(f"No se pueden descontar {cantidad} unidades. Stock actual: {self.cantidad_stock}.")
        self.cantidad_stock -= cantidad
        self.save()

    def __str__(self):
        return f"{self.nombre} ({self.marca})"

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        db_table = "productos"


# Modelo Empresas
class Empresas(models.Model):
    ruc = models.CharField(primary_key=True, max_length=13, unique=True)
    nombre = models.CharField(max_length=50, blank=False, verbose_name="Nombre de la empresa:", validators=[validacion_especial])
    direccion = models.TextField()
    telefono = models.CharField(max_length=10, validators=[validar_telefono])
    email = models.EmailField(unique=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_inicio_actividades = models.DateField(blank=True, null=True)

    def clean(self):
        if self.fecha_inicio_actividades and self.fecha_inicio_actividades > timezone.now().date():
            raise ValidationError("La fecha de inicio de actividades no puede ser en el futuro.")
        if self.fecha_inicio_actividades and self.fecha_inicio_actividades > self.fecha_creacion.date():
            raise ValidationError("La fecha de inicio de actividades no puede ser posterior a la fecha de creación.")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        db_table = "empresas"


# Modelo Proveedores
class Proveedores(models.Model):
    cedula = models.CharField(primary_key=True, max_length=10, unique=True, validators=[validar_cedula])
    nombre = models.CharField(max_length=50, blank=False, verbose_name="Nombre del proveedor:", validators=[validacion_especial])
    apellido = models.CharField(max_length=50, blank=False)
    telefono = models.CharField(max_length=10, validators=[validar_telefono])
    email = models.EmailField(unique=True)
    empresa = models.ForeignKey(Empresas, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        db_table = "proveedores"


# Modelo Factura
class Factura(models.Model):
    TIPO_FACTURA_CHOICES = (
        ("DATOS_COMPLETOS", "Con Datos Completos"),
        ("CONSUMIDOR_FINAL", "Consumidor Final"),
    )
    ESTADO_FACTURA_CHOICES = (
        ("ACTIVA", "Activa"),
        ("ANULADA", "Anulada"),
        ("DEVUELTA", "Devuelta"),
    )

    codigo_factura = models.AutoField(primary_key=True)
    fecha_factura = models.DateTimeField(auto_now_add=True)
    cliente = models.ForeignKey(Clientes, on_delete=models.CASCADE, null=True, blank=True)
    empleado = models.ForeignKey("Empleados", on_delete=models.CASCADE)
    producto = models.ForeignKey(Productos, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    iva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tipo_factura = models.CharField(max_length=20, choices=TIPO_FACTURA_CHOICES, default="DATOS_COMPLETOS")
    estado = models.CharField(max_length=10, choices=ESTADO_FACTURA_CHOICES, default="ACTIVA")

    def save(self, *args, **kwargs):
        """
        Sobrescribe el método `save` para manejar los cambios de stock
        al guardar o actualizar facturas.
        """
        # Verificar si la factura ya existe en la base de datos
        if self.pk:  # Si existe, es una actualización
            factura_prev = Factura.objects.get(pk=self.pk)

            # **1. Manejar la devolución**: Si se marca como DEVUELTA
            if self.estado == 'DEVUELTA' and factura_prev.estado != 'DEVUELTA':
                # Regresar cantidad previa al stock del producto original
                factura_prev.producto.cantidad_stock += factura_prev.cantidad
                factura_prev.producto.save()

            # **2. Cambiar producto en la factura**
            if self.producto != factura_prev.producto:
                # Regresar cantidad anterior al producto original
                factura_prev.producto.cantidad_stock += factura_prev.cantidad
                factura_prev.producto.save()

                # Restar la nueva cantidad al nuevo producto
                if self.cantidad > self.producto.cantidad_stock:
                    raise ValidationError(
                        f"No hay suficiente stock del producto '{self.producto.nombre}'."
                    )
                self.producto.cantidad_stock -= self.cantidad
                self.producto.save()

            # **3. Cambiar cantidad del producto**
            if self.cantidad != factura_prev.cantidad and self.producto == factura_prev.producto:
                diferencia = self.cantidad - factura_prev.cantidad
                if diferencia > 0:  # Si la nueva cantidad aumenta
                    if diferencia > self.producto.cantidad_stock:
                        raise ValidationError(
                            f"No hay suficiente stock del producto '{self.producto.nombre}'."
                        )
                    self.producto.cantidad_stock -= diferencia
                else:  # Si la nueva cantidad disminuye
                    self.producto.cantidad_stock += abs(diferencia)
                self.producto.save()

        else:  # Si es una nueva factura
            # Restar del stock inicial
            if self.cantidad > self.producto.cantidad_stock:
                raise ValidationError(
                    f"No hay suficiente stock del producto '{self.producto.nombre}'."
                )
            self.producto.cantidad_stock -= self.cantidad
            self.producto.save()

        # Calcular valores monetarios
        self.subtotal = self.cantidad * self.producto.precio
        self.iva = self.subtotal * Decimal(0.15)  # IVA al 15%
        self.total = self.subtotal + self.iva

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"
        db_table = "facturas"
    
    
class Empleados (models.Model):
    cedula = models.CharField(primary_key=True,max_length=10,unique=True,validators=[validar_cedula])
    nombre = models.CharField(max_length=50, blank=False, verbose_name='Nombre del Empleado : ',validators=[validacion_especial])
    apellido = models.CharField(max_length=50, blank=False)
    apellido = models.CharField(max_length=50, blank=False)
    telefono = models.CharField(max_length=10,validators=[validar_telefono])
    email = models.EmailField(unique=True)
    direccion = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_nacimiento = models.DateField()
    direccion = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_nacimiento = models.DateField()
    
    def clean(self):
        edad_minima = self.fecha_nacimiento + relativedelta(years=18)
        if edad_minima > timezone.now().date():
            raise ValidationError('El cliente debe ser mayor de 18 años.')
        
    def __str__(self):
        return f"{self.nombre} ' ' {self.apellido} "
    
    class Meta:
        verbose_name = 'Empleado :'
        verbose_name_plural = 'Empleados'
        db_table = 'Empleados'