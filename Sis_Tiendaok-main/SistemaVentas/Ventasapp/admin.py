from django.contrib import admin
from .models import Clientes,Empleados,Factura,Productos,Proveedores,Empresas
# Register your models here.

#Uso de decoradores para mejorar la presentacion en el panel de admin

@admin.register (Clientes)
class ClientesAdmin(admin.ModelAdmin):
    list_display = ('cedula', 'nombre', 'apellido', 'telefono', 'direccion', 'email')
    search_fields = ('cedula', 'nombre', 'apellido')
    list_filter = ('cedula', 'apellido')

@admin.register (Empleados)
class EmpleadosAdmin(admin.ModelAdmin):
    list_display = ('cedula', 'nombre', 'apellido', 'telefono', 'email', 'direccion', 'telefono', 'fecha_creacion','fecha_nacimiento')
    search_fields = ('cedula', 'apellido')

@admin.register (Productos)
class ProductosAdmin(admin.ModelAdmin):
    list_display = ('nombre','cantidad_stock')

@admin.register (Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ('codigo_factura','fecha_factura','cliente', 'empleado','producto','cantidad','total')

@admin.register (Proveedores)
class ProveedoresAdmin(admin.ModelAdmin):
    list_display = ('cedula','nombre','apellido') 
    
@admin.register (Empresas)
class EmpresasAdmin(admin.ModelAdmin):
    list_display = ('ruc','nombre','telefono')  
     
     
    
    