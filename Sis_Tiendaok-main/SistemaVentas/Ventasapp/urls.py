from django.urls import path
from . import views

urlpatterns = [
    path('facturas/', views.listar_facturas, name='listar_facturas'),
    path('facturas/crear/', views.crear_factura, name='crear_factura'),
    path('facturas/<int:pk>/devolver/', views.devolver_factura, name='devolver_factura'),
]
