from django.urls import path
from . import views
from . import views_stock

urlpatterns = [
    path('articulos/', views.lista_articulos, name='lista_articulos'),
    path('articulos/nuevo/', views.nuevo_articulo, name='nuevo_articulo'),
    path('articulos/<int:pk>/editar/', views.editar_articulo, name='editar_articulo'),
    path('articulos/<int:pk>/eliminar/', views.eliminar_articulo, name='eliminar_articulo'),
    path('familias/', views.lista_familias, name='lista_familias'),
    path('familias/nueva/', views.nueva_familia, name='nueva_familia'),
    path('familias/<int:pk>/editar/', views.editar_familia, name='editar_familia'),
    path('familias/<int:pk>/eliminar/', views.eliminar_familia, name='eliminar_familia'),
    path('sugerencias-reposicion/', views_stock.sugerencias_reposicion, name='sugerencias_reposicion'),
]