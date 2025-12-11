from django.shortcuts import render
from django.db import models
from .models import Articulo, Stock

def sugerencias_reposicion(request):
    articulos_bajo_minimo = Articulo.objects.filter(stock__fisico__lte=models.F('stock__minimo'))
    return render(request, 'inventario/sugerencias_reposicion.html', {
        'articulos': articulos_bajo_minimo
    })
