from django.contrib import admin
from django import forms
from .models import Clientes, Empleados, Factura, Productos, Proveedores, Empresas


class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

      

    def clean_cliente(self):
        """Validar que el cliente sea obligatorio para facturas de tipo 'DATOS_COMPLETOS'."""
        cliente = self.cleaned_data.get('cliente')
        tipo_factura = self.cleaned_data.get('tipo_factura')

        if tipo_factura == 'DATOS_COMPLETOS' and not cliente:
            raise forms.ValidationError("El cliente es obligatorio para facturas con datos completos.")
        return cliente



# Clientes Admin
@admin.register(Clientes)
class ClientesAdmin(admin.ModelAdmin):
    list_display = ('cedula', 'nombre', 'apellido', 'telefono', 'direccion', 'email')
    search_fields = ('cedula', 'nombre', 'apellido')
    list_filter = ('fecha_creacion',)
    ordering = ('nombre',)
    list_per_page = 25


# Empleados Admin
@admin.register(Empleados)
class EmpleadosAdmin(admin.ModelAdmin):
    list_display = ('cedula', 'nombre', 'apellido', 'telefono', 'email', 'direccion', 'fecha_creacion', 'fecha_nacimiento')
    search_fields = ('cedula', 'nombre', 'apellido')
    list_filter = ('fecha_creacion', 'fecha_nacimiento')
    ordering = ('nombre',)
    list_per_page = 25


# Productos Admin
@admin.register(Productos)
class ProductosAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'marca', 'categoria', 'precio', 'cantidad_stock')
    search_fields = ('codigo', 'nombre', 'marca')
    list_filter = ('categoria', 'fecha_creacion')
    ordering = ('nombre',)
    list_per_page = 25
    actions = ['actualizar_stock']

    def actualizar_stock(self, request, queryset):
        """Ejemplo de acción personalizada: Actualizar stock."""
        for producto in queryset:
            producto.cantidad_stock += 10  # Incrementar stock en 10 unidades
            producto.save()
        self.message_user(request, "El stock de los productos seleccionados se ha actualizado correctamente.")
    actualizar_stock.short_description = "Actualizar stock (+10)"


# Factura Admin
@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    form = FacturaForm
    list_display = ('codigo_factura', 'fecha_factura', 'tipo_factura', 'get_cliente_nombre', 'empleado', 'producto', 'cantidad', 'total', 'estado')
    raw_id_fields = ('cliente', 'empleado', 'producto')
    search_fields = ('codigo_factura', 'cliente__nombre', 'producto__nombre')
    list_filter = ('fecha_factura', 'tipo_factura', 'estado')
    ordering = ('-fecha_factura',)
    list_per_page = 25
    actions = ['anular_factura', 'devolver_factura']

    class Media:
        js = ('js/factura_admin.js',)

    def get_cliente_nombre(self, obj):
        """Devuelve el nombre del cliente o 'Consumidor Final'."""
        return obj.cliente.nombre if obj.cliente else "Consumidor Final"
    get_cliente_nombre.short_description = 'Nombre del Cliente'

    def get_readonly_fields(self, request, obj=None):
        """Deshabilitar campos según condiciones."""
        if obj:  # Al editar una factura existente
            if obj.tipo_factura == 'CONSUMIDOR_FINAL':
                return self.readonly_fields + ('cliente', 'estado')  # Bloquear cliente y estado
        return self.readonly_fields + ('estado',)  # Ocultar estado al crear

    def anular_factura(self, request, queryset):
        """Anular las facturas seleccionadas."""
        for factura in queryset:
            if factura.estado != 'ACTIVA':
                self.message_user(request, f"La factura {factura.codigo_factura} no puede ser anulada porque no está activa.", level="error")
                continue
            factura.producto.cantidad_stock += factura.cantidad
            factura.producto.save()
            factura.estado = 'ANULADA'
            factura.save()
        self.message_user(request, "La(s) factura(s) seleccionada(s) se han anulado correctamente.")
    anular_factura.short_description = 'Anular factura seleccionada'

    def devolver_factura(self, request, queryset):
        """Devolver las facturas seleccionadas."""
        for factura in queryset:
            if factura.estado != 'ACTIVA':
                self.message_user(request, f"La factura {factura.codigo_factura} no puede ser devuelta porque no está activa.", level="error")
                continue
            factura.producto.cantidad_stock += factura.cantidad
            factura.producto.save()
            factura.estado = 'DEVUELTA'
            factura.save()
        self.message_user(request, "La(s) factura(s) seleccionada(s) se han devuelto correctamente.")
    devolver_factura.short_description = 'Devolver factura seleccionada'


# Proveedores Admin
@admin.register(Proveedores)
class ProveedoresAdmin(admin.ModelAdmin):
    list_display = ('cedula', 'nombre', 'apellido', 'telefono', 'email', 'empresa')
    search_fields = ('cedula', 'nombre', 'apellido', 'email')
    list_filter = ('empresa',)
    ordering = ('nombre',)
    list_per_page = 25


# Empresas Admin
@admin.register(Empresas)
class EmpresasAdmin(admin.ModelAdmin):
    list_display = ('ruc', 'nombre', 'telefono', 'email', 'fecha_creacion')
    search_fields = ('ruc', 'nombre', 'email')
    list_filter = ('fecha_creacion',)
    ordering = ('nombre',)
    list_per_page = 25
