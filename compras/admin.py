from django.contrib import admin
from .models import SolicitudRequisicion, OrdenCompra, OrdenCompraDetalle, RecepcionMercancia, RecepcionDetalle, FacturaProveedor

admin.site.register(SolicitudRequisicion)
admin.site.register(OrdenCompra)
admin.site.register(OrdenCompraDetalle)
admin.site.register(RecepcionMercancia)
admin.site.register(RecepcionDetalle)
admin.site.register(FacturaProveedor)
