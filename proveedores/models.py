from django.db import models


# --- Datos Maestros ---
class Proveedor(models.Model):
    razon_social = models.CharField(max_length=150)
    nombre_comercial = models.CharField(max_length=150, blank=True)
    id_fiscal = models.CharField(max_length=30, verbose_name="RUC/RUT/NIF")
    direccion_fiscal = models.CharField(max_length=200)
    direccion_almacen = models.CharField(max_length=200, blank=True)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    estado = models.CharField(max_length=20, choices=[
        ("activo", "Activo"),
        ("inactivo", "Inactivo"),
        ("bloqueado", "Bloqueado"),
        ("en_prueba", "En prueba")
    ], default="activo")
    logo = models.ImageField(upload_to="proveedores/logos/", blank=True, null=True, verbose_name="Logo")
    rating = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True, verbose_name="Rating (1-5)")
    from django.utils import timezone
    fecha_alta = models.DateField(default=timezone.now, verbose_name="Fecha de alta")

    def __str__(self):
        return self.razon_social

# --- Contactos Clave ---
class ContactoProveedor(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name="contactos")
    nombre = models.CharField(max_length=100)
    cargo = models.CharField(max_length=50)
    email = models.EmailField()
    telefono = models.CharField(max_length=20, blank=True)
    extension = models.CharField(max_length=10, blank=True)

# --- Información Financiera y Legal ---
class DatosBancarios(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name="bancos")
    banco = models.CharField(max_length=100)
    numero_cuenta = models.CharField(max_length=50)
    tipo_cuenta = models.CharField(max_length=30)
    titular = models.CharField(max_length=100)
    codigo_interbancario = models.CharField(max_length=50, blank=True)

class CondicionPago(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name="condiciones_pago")
    condicion = models.CharField(max_length=30, choices=[
        ("contado", "Contado"),
        ("credito_15", "Crédito 15 días"),
        ("credito_30", "Crédito 30 días"),
        ("credito_60", "Crédito 60 días"),
        ("anticipo", "Anticipo requerido")
    ])

class DocumentoLegal(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name="documentos_legales")
    nombre = models.CharField(max_length=100)
    archivo = models.FileField(upload_to="documentos_legales/")

class Moneda(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name="monedas")
    moneda = models.CharField(max_length=20)

# --- Catálogo y Precios ---
class ProductoProveedor(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name="productos")
    nombre = models.CharField(max_length=100)
    codigo_interno = models.CharField(max_length=50)
    codigo_proveedor = models.CharField(max_length=50)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    lead_time = models.PositiveIntegerField(help_text="Días promedio de entrega")
    moq = models.PositiveIntegerField(help_text="Mínimo de compra")

    def precio_final(self):
        if self.descuento:
            return float(self.precio_unitario) * (1 - float(self.descuento)/100)
        return self.precio_unitario

class HistorialPrecio(models.Model):
    producto = models.ForeignKey(ProductoProveedor, on_delete=models.CASCADE, related_name="historial_precios")
    fecha = models.DateField(auto_now_add=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

# --- Evaluación y Desempeño ---
class ScorecardProveedor(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name="scorecards")
    calidad = models.DecimalField(max_digits=4, decimal_places=2)
    puntualidad = models.DecimalField(max_digits=4, decimal_places=2)
    cumplimiento = models.DecimalField(max_digits=4, decimal_places=2)
    fecha = models.DateField(auto_now_add=True)

class IncidenteProveedor(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name="incidentes")
    fecha = models.DateField(auto_now_add=True)
    descripcion = models.TextField()

# --- Historial de Transacciones ---

# --- Detalle de Orden de Compra ---

# El modelo DetalleOrdenCompra dependía de inventario.Articulo, se elimina para restaurar solo proveedores.

class FacturaProveedor(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name="facturas")
    numero = models.CharField(max_length=50)
    estado = models.CharField(max_length=20, choices=[
        ("pendiente", "Pendiente"),
        ("pagada", "Pagada")
    ])
    fecha = models.DateField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)

class DevolucionProveedor(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name="devoluciones")
    fecha = models.DateField()
    motivo = models.TextField()
    nota_credito = models.CharField(max_length=50, blank=True)
