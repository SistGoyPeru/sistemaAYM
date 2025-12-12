from django.db import models
from django.contrib.auth.models import User
from inventario.models import Articulo, Almacen
from proveedores.models import Proveedor

class SolicitudRequisicion(models.Model):
    PRIORIDAD_CHOICES = [
        ("alta", "Alta"),
        ("media", "Media"),
        ("baja", "Baja"),
    ]
    solicitante = models.ForeignKey(User, on_delete=models.PROTECT, related_name="requisiciones")
    fecha = models.DateField(auto_now_add=True)
    producto = models.ForeignKey(Articulo, on_delete=models.PROTECT, related_name="requisiciones")
    cantidad = models.PositiveIntegerField()
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default="media")
    estado = models.CharField(max_length=15, choices=[
        ("pendiente", "Pendiente"),
        ("aprobada", "Aprobada"),
        ("rechazada", "Rechazada")
    ], default="pendiente")
    observaciones = models.TextField(blank=True)
    fecha_revision = models.DateTimeField(null=True, blank=True)
    gerente = models.ForeignKey(User, on_delete=models.PROTECT, related_name="revisiones_requisiciones", null=True, blank=True)

    def __str__(self):
        return f"{self.producto} x {self.cantidad} ({self.solicitante}) - {self.estado}"

class OrdenCompra(models.Model):
    ESTADO_CHOICES = [
        ("borrador", "Borrador"),
        ("pendiente_autorizacion", "Pendiente de Autorización"),
        ("autorizada", "Autorizada"),
        ("enviada", "Enviada/Confirmada"),
        ("recibida_parcial", "Recibida Parcial"),
        ("recibida_total", "Recibida Total"),
        ("cancelada", "Cancelada"),
    ]
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name="ordenes_compra")
    fecha_emision = models.DateField(auto_now_add=True)
    fecha_entrega_esperada = models.DateField()
    almacen_destino = models.ForeignKey(Almacen, on_delete=models.PROTECT, related_name="ordenes_compra")
    condiciones_pago = models.CharField(max_length=100, blank=True)
    moneda = models.CharField(max_length=20, blank=True)
    estado = models.CharField(max_length=30, choices=ESTADO_CHOICES, default="borrador")
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    impuestos = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    observaciones = models.TextField(blank=True)
    solicitud_requisicion = models.ForeignKey('SolicitudRequisicion', on_delete=models.SET_NULL, null=True, blank=True, related_name="ordenes_compra")

class AutorizacionOC(models.Model):
    orden = models.ForeignKey(OrdenCompra, on_delete=models.CASCADE, related_name="autorizaciones")
    nivel = models.PositiveIntegerField()
    responsable = models.ForeignKey(User, on_delete=models.PROTECT, related_name="autorizaciones_oc")
    autorizado = models.BooleanField(null=True, blank=True)
    fecha = models.DateTimeField(auto_now=True)
    comentario = models.TextField(blank=True)

    class Meta:
        unique_together = ("orden", "nivel")
        ordering = ["nivel"]

    def __str__(self):
        return f"OC #{self.orden.id} - Nivel {self.nivel} - {self.responsable}"

    def __str__(self):
        return f"OC #{self.id} - {self.proveedor} ({self.estado})"

class OrdenCompraDetalle(models.Model):
    orden = models.ForeignKey(OrdenCompra, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Articulo, on_delete=models.PROTECT)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    unidad_medida = models.CharField(max_length=20)
    costo_unitario = models.DecimalField(max_digits=14, decimal_places=4)
    impuesto = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.producto} x {self.cantidad} en OC #{self.orden.id}"

class RecepcionMercancia(models.Model):
    orden = models.ForeignKey(OrdenCompra, on_delete=models.CASCADE, related_name="recepciones")
    fecha_recepcion = models.DateField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"Recepción OC #{self.orden.id} - {self.fecha_recepcion}"

class RecepcionDetalle(models.Model):
    recepcion = models.ForeignKey(RecepcionMercancia, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Articulo, on_delete=models.PROTECT)
    cantidad_recibida = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_danada = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unidad_medida = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.producto} - Recibido: {self.cantidad_recibida} (Dañado: {self.cantidad_danada})"

class FacturaProveedor(models.Model):
    orden = models.ForeignKey(OrdenCompra, on_delete=models.PROTECT, related_name="facturas")
    numero_factura = models.CharField(max_length=50)
    fecha_emision = models.DateField()
    monto_factura = models.DecimalField(max_digits=14, decimal_places=2)
    archivo = models.FileField(upload_to="facturas_proveedor/", blank=True, null=True)
    validada = models.BooleanField(default=False)
    diferencia_autorizada = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"Factura {self.numero_factura} - OC #{self.orden.id}"
