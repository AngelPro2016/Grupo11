from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Factura, Productos
from .admin import FacturaForm


# Vista para listar las facturas
def listar_facturas(request):
    facturas = Factura.objects.all()
    return render(request, 'facturas/listar_facturas.html', {'facturas': facturas})


# Vista para crear una nueva factura
def crear_factura(request):
    if request.method == 'POST':
        form = FacturaForm(request.POST)
        if form.is_valid():
            factura = form.save()
            return redirect('listar_facturas')
    else:
        form = FacturaForm()
    return render(request, 'facturas/crear_factura.html', {'form': form})


# Vista para devolver productos de la factura
def devolver_factura(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    if factura.estado != 'DEVUELTA':
        # Restablecer el stock del producto relacionado
        factura.producto.cantidad_stock += factura.cantidad
        factura.producto.save()
        factura.estado = 'DEVUELTA'
        factura.save()
        return JsonResponse({'success': True, 'message': 'Producto devuelto correctamente.'})
    return JsonResponse({'success': False, 'message': 'La factura ya estaba devuelta.'})
