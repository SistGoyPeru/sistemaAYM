from django import forms
from .models import SolicitudRequisicion, OrdenCompra, OrdenCompraDetalle, RecepcionMercancia, RecepcionDetalle, FacturaProveedor

class SolicitudRequisicionForm(forms.ModelForm):
    class Meta:
        model = SolicitudRequisicion
        fields = ['producto', 'cantidad', 'prioridad', 'observaciones']

class OrdenCompraForm(forms.ModelForm):
    class Meta:
        model = OrdenCompra
        fields = [
            'proveedor',
            'fecha_entrega_esperada',
            'almacen_destino',
            'condiciones_pago',
            'moneda',
            'estado',
            'subtotal',
            'impuestos',
            'total',
            'observaciones',
            'solicitud_requisicion',
        ]

class OrdenCompraDetalleForm(forms.ModelForm):
    class Meta:
        model = OrdenCompraDetalle
        fields = ['producto', 'cantidad', 'unidad_medida', 'costo_unitario']

class RecepcionMercanciaForm(forms.ModelForm):
    class Meta:
        model = RecepcionMercancia
        fields = ['orden', 'observaciones']

class RecepcionDetalleForm(forms.ModelForm):
    class Meta:
        model = RecepcionDetalle
        fields = ['producto', 'cantidad_recibida', 'cantidad_danada', 'unidad_medida']

class FacturaProveedorForm(forms.ModelForm):
    class Meta:
        model = FacturaProveedor
        fields = ['orden', 'numero_factura', 'fecha_emision', 'monto_factura', 'archivo', 'observaciones']
