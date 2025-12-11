from django.urls import path
from .views_orden import nueva_orden_compra, lista_ordenes_compra

urlpatterns = [
    path('ordenes/', lista_ordenes_compra, name='lista_ordenes_compra'),
    path('ordenes/nueva/', nueva_orden_compra, name='nueva_orden_compra'),
]
