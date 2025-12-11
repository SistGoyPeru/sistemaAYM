
from django.shortcuts import render, redirect, get_object_or_404
from .models import OrdenCompra, DetalleOrdenCompra
from .forms_orden import OrdenCompraForm
from .forms_detalle_orden import DetalleOrdenCompraForm
from inventario.models import Articulo

def nueva_orden_compra(request):
    if request.method == 'POST':
        form = OrdenCompraForm(request.POST)
        if form.is_valid():
            orden = form.save()
            return redirect('agregar_detalles_orden', pk=orden.pk)
    else:
        form = OrdenCompraForm()
    return render(request, 'proveedores/form_orden_compra.html', {'form': form})


# Vista para agregar detalles a una orden de compra y actualizar costo promedio
def agregar_detalles_orden(request, pk):
    orden = get_object_or_404(OrdenCompra, pk=pk)
    if request.method == 'POST':
        form = DetalleOrdenCompraForm(request.POST)
        if form.is_valid():
            detalle = form.save(commit=False)
            detalle.orden = orden
            detalle.save()
            # Actualizar costo promedio del artículo
            articulo = detalle.articulo
            compras_previas = DetalleOrdenCompra.objects.filter(articulo=articulo).exclude(pk=detalle.pk)
            total_cantidad = sum([d.cantidad for d in compras_previas]) + detalle.cantidad
            total_costo = sum([d.cantidad * d.precio_unitario for d in compras_previas]) + (detalle.cantidad * detalle.precio_unitario)
            if total_cantidad > 0:
                articulo.costo_promedio = total_costo / total_cantidad
                articulo.save()
            return redirect('agregar_detalles_orden', pk=orden.pk)
    else:
        form = DetalleOrdenCompraForm()
    detalles = DetalleOrdenCompra.objects.filter(orden=orden)
    return render(request, 'proveedores/form_detalle_orden.html', {'orden': orden, 'form': form, 'detalles': detalles})

def lista_ordenes_compra(request):
    from django.db.models import Q
    from django.http import HttpResponse
    import openpyxl
    q = request.GET.get('q', '')
    estado = request.GET.get('estado', '')
    ordenes = OrdenCompra.objects.select_related('proveedor').all()
    if q:
        ordenes = ordenes.filter(Q(codigo__icontains=q) | Q(proveedor__razon_social__icontains=q))
    if estado:
        ordenes = ordenes.filter(estado=estado)
    if 'exportar' in request.GET:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Órdenes de Compra"
        ws.append(["Código", "Proveedor", "Estado", "Fecha"])
        for o in ordenes:
            ws.append([
                o.codigo, o.proveedor.razon_social, o.get_estado_display(), o.fecha
            ])
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="ordenes_compra.xlsx"'
        wb.save(response)
        return response
    return render(request, 'proveedores/lista_ordenes_compra.html', {
        'ordenes': ordenes,
        'q': q,
        'estado_sel': estado,
    })
