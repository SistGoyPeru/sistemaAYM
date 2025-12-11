from django import forms
from .models import Articulo, Familia, FichaTecnica, Stock

class FamiliaForm(forms.ModelForm):
    class Meta:
        model = Familia
        fields = ['nombre', 'descripcion']

class FichaTecnicaForm(forms.ModelForm):
    class Meta:
        model = FichaTecnica
        fields = '__all__'

class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['fisico', 'comprometido', 'minimo', 'maximo']

class ArticuloForm(forms.ModelForm):
    class Meta:
        model = Articulo
        fields = [
            'nombre', 'codigo', 'tipo', 'familia', 'descripcion', 'unidad_medida', 'activo', 'ficha_tecnica',
            'costo_promedio', 'precio_base', 'precio_mayorista', 'precio_distribuidor', 'tipo_impuesto'
        ]
