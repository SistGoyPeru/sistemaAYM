"""
Archivo de URLs principal para el proyecto Django sistemaAyM.
"""



from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def root_redirect(request):
    return redirect('/proveedores/')

from compras.views import dashboard

urlpatterns = [
    path('', root_redirect),
    path('dashboard/', dashboard, name='dashboard'),
    path('admin/', admin.site.urls),
    path('proveedores/', include('proveedores.urls')),
    path('inventario/', include('inventario.urls')),
    path('compras/', include('compras.urls')),
]
