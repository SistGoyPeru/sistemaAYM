"""
Archivo de URLs principal para el proyecto Django sistemaAyM.
"""



from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def root_redirect(request):
    return redirect('/proveedores/')

urlpatterns = [
    path('', root_redirect),
    path('admin/', admin.site.urls),
    path('proveedores/', include('proveedores.urls')),
]
