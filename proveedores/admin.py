from django.contrib import admin
from .models import (
    Proveedor, ContactoProveedor, DatosBancarios, CondicionPago, DocumentoLegal, Moneda,
    ProductoProveedor, HistorialPrecio, ScorecardProveedor, IncidenteProveedor,
    FacturaProveedor, DevolucionProveedor
)


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('razon_social', 'nombre_comercial', 'id_fiscal', 'telefono', 'email', 'estado')

@admin.register(ContactoProveedor)
class ContactoProveedorAdmin(admin.ModelAdmin):
    list_display = ('proveedor', 'nombre', 'cargo', 'email', 'telefono', 'extension')

@admin.register(DatosBancarios)
class DatosBancariosAdmin(admin.ModelAdmin):
    list_display = ('proveedor', 'banco', 'numero_cuenta', 'tipo_cuenta', 'titular', 'codigo_interbancario')

@admin.register(CondicionPago)
class CondicionPagoAdmin(admin.ModelAdmin):
    list_display = ('proveedor', 'condicion')

@admin.register(DocumentoLegal)
class DocumentoLegalAdmin(admin.ModelAdmin):
    list_display = ('proveedor', 'nombre', 'archivo')

@admin.register(Moneda)
class MonedaAdmin(admin.ModelAdmin):
    list_display = ('proveedor', 'moneda')

@admin.register(ProductoProveedor)
class ProductoProveedorAdmin(admin.ModelAdmin):
    list_display = ('proveedor', 'nombre', 'codigo_interno', 'codigo_proveedor', 'precio_unitario', 'descuento', 'lead_time', 'moq')

@admin.register(HistorialPrecio)
class HistorialPrecioAdmin(admin.ModelAdmin):
    list_display = ('producto', 'fecha', 'precio')

@admin.register(ScorecardProveedor)
class ScorecardProveedorAdmin(admin.ModelAdmin):
    list_display = ('proveedor', 'calidad', 'puntualidad', 'cumplimiento', 'fecha')

@admin.register(IncidenteProveedor)
class IncidenteProveedorAdmin(admin.ModelAdmin):
    list_display = ('proveedor', 'fecha', 'descripcion')

@admin.register(FacturaProveedor)
class FacturaProveedorAdmin(admin.ModelAdmin):
    list_display = ('proveedor', 'numero', 'estado', 'fecha', 'monto')

@admin.register(DevolucionProveedor)
class DevolucionProveedorAdmin(admin.ModelAdmin):
    list_display = ('proveedor', 'fecha', 'motivo', 'nota_credito')
