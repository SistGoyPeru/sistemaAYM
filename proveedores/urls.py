from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_proveedores, name='lista_proveedores'),
    path('nuevo/', views.nuevo_proveedor, name='nuevo_proveedor'),
    path('editar/<int:pk>/', views.editar_proveedor, name='editar_proveedor'),
    path('eliminar/<int:pk>/', views.eliminar_proveedor, name='eliminar_proveedor'),
    path('catalogo/', views.catalogo_productos, name='catalogo_productos'),
    path('detalle/<int:pk>/', views.detalle_proveedor, name='detalle_proveedor'),
    path('exportar_excel/<int:pk>/', views.exportar_proveedor_excel, name='exportar_proveedor_excel'),
]
