from django.db import models
from .choices import CATEGORIAS
from decimal import Decimal
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.core.validators import MinValueValidator, MaxValueValidator, MaxLengthValidator, MinLengthValidator
from .validadores import validacion_numeros, Validacion_letras,ValidationError, validacion_especial,validacion_especial2,validacion_especial3,validar_cedula,validar_telefono
from datetime import timedelta, date
from django.conf import settings

IVA_PERCENT = getattr(settings, 'IVA_PERCENT', Decimal("0.15"))

class Clientes(models.Model):
    cedula = models.CharField(
        primary_key=True,
        max_length=10,
        unique=True,
        validators=[validar_cedula]
    )
    nombre = models.CharField(
        max_length=50,
        blank=False,
        verbose_name='Nombre del cliente:',
        validators=[validacion_especial]
    )
    apellido = models.CharField(max_length=50, blank=False)
    telefono = models.CharField(
        max_length=10,
        validators=[validar_telefono]
    )
    email = models.EmailField(unique=True)
    direccion = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_nacimiento = models.DateField()

    def clean(self):
        edad_minima = self.fecha_nacimiento + relativedelta(years=18)
        if edad_minima > timezone.now().date():
            raise ValidationError('El cliente debe ser mayor de 18 años.')

    def str(self):
        return f"{self.nombre} {self.apellido}"

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        db_table = 'ventas_clientes'


class Productos(models.Model):
    codigo = models.CharField(primary_key=True, max_length=10, unique=True)
    nombre = models.CharField(max_length=50, blank=False, verbose_name=' Nombre del producto : ',validators=[validacion_especial])
    marca = models.CharField(max_length=50, unique=True, validators=[validacion_especial])
    caracteristicas_categoria = models.CharField(max_length=100, choices=CATEGORIAS)
    precio = models.DecimalField(max_digits=10, decimal_places=2, help_text='ingresa valores con decimales', verbose_name='Precio del producto : ')
    cantidad_stock = models.IntegerField(verbose_name='Cantidad en stock : ')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_elaboracion = models.DateField()
    fecha_vencimiento = models.DateField()

    def clean(self):
        # fechas iguales
        if self.fecha_vencimiento == self.fecha_elaboracion:
            raise ValidationError('La fecha de vencimiento y la fecha de elaboración no pueden ser la misma.')
        
        # no debe estar distanciados por 5
        max_diferencia = timedelta(days=5*365)  # 5 a;os
        if self.fecha_vencimiento - self.fecha_elaboracion > max_diferencia:
            raise ValidationError('La fecha de elaboración no debe tener una diferencia mayor a 5 años con la fecha de vencimiento.')
    def save(self, *args, **kwargs):
        # Ejecutar validación personalizada antes de guardar
        self.clean()
        super().save(*args, **kwargs)

    def actualizar_stock(self, cantidad):
        """Actualiza el stock del producto verificando que no sea menor a cero."""
        if cantidad > self.cantidad_stock:
            raise ValueError(f"No se puede descontar {cantidad} unidades del producto '{self.nombre}' porque solo hay {self.cantidad_stock} disponibles.")
        self.cantidad_stock -= cantidad
        self.save()

    def __str__(self):
        return f"{self.nombre}  {self.marca} "

    class Meta:
        verbose_name = 'Producto :'
        verbose_name_plural = 'Productos'
        db_table = 'Productos'


class Empresas(models.Model):
    ruc = models.CharField(primary_key=True, max_length=13, unique=True)
    nombre = models.CharField(max_length=50, blank=False, verbose_name='Nombre de la empresa : ', validators=[validacion_especial])
    direccion = models.TextField()
    telefono = models.CharField(max_length=10, validators=[validar_telefono])
    email = models.EmailField(unique=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_inicio_actividades = models.DateField(blank=True, null=True)

    def clean(self):
        # Validar que fecha_inicio_actividades no sea futura
        if self.fecha_inicio_actividades and self.fecha_inicio_actividades > timezone.now().date():
            raise ValidationError({
                'fecha_inicio_actividades': 'La fecha de inicio de actividades no puede ser en el futuro.'
            })
        
        if self.fecha_inicio_actividades and self.fecha_creacion:
            if self.fecha_inicio_actividades > self.fecha_creacion:
                raise ValidationError({
                'fecha_inicio_actividades': 'La fecha de inicio de actividades no puede ser posterior a la fecha de creación.'
            })

    def __str__(self):
        return f"{self.nombre} "

    class Meta:
        verbose_name = 'Empresa :'
        verbose_name_plural = 'Empresas'
        db_table = 'Empresas'

class Proveedores (models.Model):
    cedula = models.CharField(primary_key=True, max_length=10, unique=True,validators=[validar_cedula])
    nombre = models.CharField(max_length=50, blank=False, verbose_name='Nombre del proveedor : ',validators=[validacion_especial])
    apellido = models.CharField(max_length=50, blank=False)
    telefono = models.CharField(max_length=10,validators=[validar_telefono])
    email = models.EmailField(unique=True)
    empresa = models.ForeignKey(Empresas, on_delete= models.CASCADE)
    def __str__(self):
        return f"{self.nombre} ' ' {self.apellido} "
    class Meta:
        verbose_name = 'Proveedor '
        verbose_name_plural = 'Proveedores'
        db_table = 'Proveedores'

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

class Factura(models.Model):
    TIPO_FACTURA_CHOICES = (
        ('DATOS_COMPLETOS', 'Con Datos Completos'),
        ('CONSUMIDOR_FINAL', 'Consumidor Final'),
    )

    codigo_factura = models.AutoField(primary_key=True)
    fecha_factura = models.DateTimeField(auto_now_add=True)
    cliente = models.ForeignKey(Clientes, on_delete=models.CASCADE, null=True, blank=True)
    empleado = models.ForeignKey(Empleados, on_delete=models.CASCADE)
    producto = models.ForeignKey(Productos, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=True, default=0)
    iva = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)
    tipo_factura = models.CharField(
        max_length=20,
        choices=TIPO_FACTURA_CHOICES,
        default='DATOS_COMPLETOS'
    )
    estado = models.CharField(
        max_length=10,
        choices=(
            ('ACTIVA', 'Activa'),
            ('ANULADA', 'Anulada'),
            ('DEVUELTA', 'Devuelta'),
        ),
        default='ACTIVA'
    )

    def save(self, *args, **kwargs):
        if self.estado == 'ACTIVA':
            self.subtotal = self.cantidad * self.producto.precio
            self.iva = self.subtotal * Decimal(0.15)
            self.total = self.subtotal + self.iva
        super().save(*args, **kwargs)











