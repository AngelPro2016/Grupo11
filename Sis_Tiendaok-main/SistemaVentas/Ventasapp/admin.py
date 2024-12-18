from django.contrib import admin
from django import forms
from .models import Clientes, Empleados, Factura, Productos, Proveedores, Empresas

# Formulario personalizado para Factura
class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.ak:
            self.fields['estado'].widget = forms.HiddenInput()
            self.fields['estado'].initial = 'Activa'  
        # Deshabilitar cliente si es "Consumidor Final"
        if self.instance and self.instance.tipo_factura == 'CONSUMIDOR_FINAL':
            self.fields['cliente'].disabled = True  # Bloquear el campo cliente
        else:
            self.fields['cliente'].disabled = False


# Clientes Admin
@admin.register(Clientes)
class ClientesAdmin(admin.ModelAdmin):
    list_display = ('cedula', 'nombre', 'apellido', 'telefono', 'direccion', 'email')
    search_fields = ('cedula', 'nombre', 'apellido')
    list_filter = ('cedula', 'apellido')


# Empleados Admin
@admin.register(Empleados)
class EmpleadosAdmin(admin.ModelAdmin):
    list_display = ('cedula', 'nombre', 'apellido', 'telefono', 'email', 'direccion', 'fecha_creacion', 'fecha_nacimiento')
    search_fields = ('cedula', 'apellido')


# Productos Admin
@admin.register(Productos)
class ProductosAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'cantidad_stock')


# Factura Admin
@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    form = FacturaForm
    list_display = ('codigo_factura', 'fecha_factura', 'tipo_factura', 'get_cliente_nombre', 'empleado', 'producto', 'cantidad', 'total', 'estado')
    raw_id_fields = ('cliente', 'empleado', 'producto')
    search_fields = ('codigo_factura', 'cliente__nombre', 'producto__nombre')
    actions = ['anular_factura', 'devolver_factura']
    
    class Media:
        js = ('js/factura_admin.js',)

    def get_cliente_nombre(self, obj):
        """Devuelve el nombre del cliente o 'Consumidor Final'."""
        return obj.cliente.nombre if obj.cliente else "Consumidor Final"
    get_cliente_nombre.short_description = 'Nombre del Cliente'

    def get_readonly_fields(self, request, obj=None):
        """Deshabilitar estado y cliente según tipo de factura."""
        if obj:  # Al editar una factura existente
            if obj.tipo_factura == 'CONSUMIDOR_FINAL':
                return self.readonly_fields + ('cliente', 'estado')  # Bloquear cliente y estado
            return self.readonly_fields
        return self.readonly_fields + ('estado',)  # Ocultar estado al crear

    def anular_factura(self, request, queryset):
        """Anular las facturas seleccionadas."""
        for factura in queryset:
            if factura.estado != 'ACTIVA':
                self.message_user(request, f"La factura {factura.codigo_factura} no puede ser anulada porque no está activa.", level="error")
                continue
            if factura.tipo_factura != 'CON_DATOS':
                self.message_user(request, f"No se puede anular la factura {factura.codigo_factura}. Solo facturas con datos pueden ser anuladas.", level="error")
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
            if factura.tipo_factura != 'CON_DATOS':
                self.message_user(request, f"No se puede devolver la factura {factura.codigo_factura}. Solo facturas con datos pueden ser devueltas.", level="error")
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
    list_display = ('cedula', 'nombre', 'apellido')


# Empresas Admin
@admin.register(Empresas)
class EmpresasAdmin(admin.ModelAdmin):
    list_display = ('ruc', 'nombre', 'telefono')

