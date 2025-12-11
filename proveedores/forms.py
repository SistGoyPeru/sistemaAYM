from django import forms
from django.forms import inlineformset_factory
from .models import Proveedor, DatosBancarios, CondicionPago, DocumentoLegal, Moneda, ProductoProveedor, IncidenteProveedor
IncidenteProveedorFormSet = inlineformset_factory(
    Proveedor, IncidenteProveedor,
    fields=['descripcion'],
    extra=1, can_delete=True
)
ProductoProveedorFormSet = inlineformset_factory(
    Proveedor, ProductoProveedor,
    fields=['nombre', 'codigo_interno', 'codigo_proveedor', 'precio_unitario', 'descuento', 'lead_time', 'moq'],
    extra=1, can_delete=True
)

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = '__all__'

DatosBancariosFormSet = inlineformset_factory(
    Proveedor, DatosBancarios, fields=['banco', 'numero_cuenta', 'tipo_cuenta', 'titular', 'codigo_interbancario'], extra=1, can_delete=True
)
CondicionPagoFormSet = inlineformset_factory(
    Proveedor, CondicionPago, fields=['condicion'], extra=1, can_delete=True
)
DocumentoLegalFormSet = inlineformset_factory(
    Proveedor, DocumentoLegal, fields=['nombre', 'archivo'], extra=1, can_delete=True
)
MonedaFormSet = inlineformset_factory(
    Proveedor, Moneda, fields=['moneda'], extra=1, can_delete=True
)
