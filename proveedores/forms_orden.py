from django import forms
from .models import OrdenCompra

class OrdenCompraForm(forms.ModelForm):
    class Meta:
        model = OrdenCompra
        fields = ['proveedor', 'codigo', 'estado', 'fecha']

    def clean_proveedor(self):
        proveedor = self.cleaned_data['proveedor']
        if proveedor.estado != 'activo':
            raise forms.ValidationError('Solo se pueden crear órdenes de compra a proveedores activos.')
        return proveedor
