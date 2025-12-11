from django.db import models
from proveedores.models import Proveedor

class ProductoProveedor(models.Model):
    articulo = models.ForeignKey('Articulo', on_delete=models.CASCADE, related_name='proveedores')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='productos_suministrados')
    codigo_proveedor = models.CharField(max_length=50, blank=True, verbose_name="Código del Proveedor")
    ultimo_costo = models.DecimalField(max_digits=14, decimal_places=4, default=0, verbose_name="Último Costo de Compra")

    class Meta:
        unique_together = ('articulo', 'proveedor')

    def __str__(self):
        return f"{self.articulo} - {self.proveedor} ({self.codigo_proveedor})"
class Almacen(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    direccion = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.nombre

class Ubicacion(models.Model):
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE, related_name='ubicaciones')
    pasillo = models.CharField(max_length=10)
    estante = models.CharField(max_length=10)
    nivel = models.CharField(max_length=10)
    caja = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return f"{self.almacen.nombre} - Pasillo {self.pasillo} Estante {self.estante} Nivel {self.nivel} Caja {self.caja}"

# Stock por almacén y ubicación
class StockUbicacion(models.Model):
    articulo = models.ForeignKey('Articulo', on_delete=models.CASCADE, related_name='stocks_ubicacion')
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE, related_name='stocks')
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, null=True, blank=True, related_name='stocks')
    cantidad = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('articulo', 'almacen', 'ubicacion')

    def __str__(self):
        return f"{self.articulo} en {self.almacen} ({self.ubicacion}): {self.cantidad}"
class Stock(models.Model):
    articulo = models.OneToOneField('Articulo', on_delete=models.CASCADE, related_name='stock')
    fisico = models.PositiveIntegerField(default=0, verbose_name="Stock Físico")
    comprometido = models.PositiveIntegerField(default=0, verbose_name="Stock Comprometido")
    disponible = models.PositiveIntegerField(default=0, verbose_name="Stock Disponible")
    minimo = models.PositiveIntegerField(default=0, verbose_name="Stock Mínimo")
    maximo = models.PositiveIntegerField(default=0, verbose_name="Stock Máximo")

    def save(self, *args, **kwargs):
        self.disponible = max(self.fisico - self.comprometido, 0)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Stock de {self.articulo.nombre} ({self.fisico} disp. {self.disponible})"
class FichaTecnica(models.Model):
    sku = models.CharField(max_length=30, unique=True, verbose_name="Código SKU")
    descripcion = models.CharField(max_length=200, verbose_name="Descripción")
    unidad_compra = models.CharField(max_length=30, verbose_name="Unidad de Compra")
    unidad_consumo = models.CharField(max_length=30, verbose_name="Unidad de Consumo/Venta")
    factor_conversion = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Factor de Conversión")
    talla = models.CharField(max_length=10, blank=True, null=True, verbose_name="Talla")
    color = models.CharField(max_length=30, blank=True, null=True, verbose_name="Color")
    material = models.CharField(max_length=50, blank=True, null=True, verbose_name="Material")
    imagen = models.ImageField(upload_to="fichas/", blank=True, null=True, verbose_name="Imagen referencial")

    def __str__(self):
        return f"{self.sku} - {self.descripcion}"
from django.db import models

class Familia(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

class TipoArticulo(models.TextChoices):
    MATERIA_PRIMA = 'materia_prima', 'Materia Prima / Insumo'
    PRODUCTO_TERMINADO = 'producto_terminado', 'Producto Terminado'
    SERVICIO = 'servicio', 'Servicio'

class Articulo(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=50, unique=True)
    tipo = models.CharField(max_length=20, choices=TipoArticulo.choices)
    familia = models.ForeignKey(Familia, on_delete=models.PROTECT, related_name='articulos')
    descripcion = models.TextField(blank=True)
    unidad_medida = models.CharField(max_length=20, default='unidad')
    activo = models.BooleanField(default=True)
    ficha_tecnica = models.OneToOneField('FichaTecnica', on_delete=models.CASCADE, blank=True, null=True, related_name='articulo')

    # Costos y precios
    costo_promedio = models.DecimalField(max_digits=14, decimal_places=4, default=0, verbose_name="Costo Promedio")
    precio_base = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name="Precio Base")
    precio_mayorista = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name="Precio Mayorista")
    precio_distribuidor = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name="Precio Distribuidor")

    class TipoImpuesto(models.TextChoices):
        IVA = 'iva', 'IVA/IGV'
        EXENTO = 'exento', 'Exento'

    tipo_impuesto = models.CharField(max_length=10, choices=TipoImpuesto.choices, default=TipoImpuesto.IVA, verbose_name="Tipo de Impuesto")

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"
