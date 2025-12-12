
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import AutorizacionOC, OrdenCompra
from django.db import models

# Vista para autorizar/rechazar OC (multinivel)
@login_required
def orden_compra_autorizar(request, pk):
    oc = get_object_or_404(OrdenCompra, pk=pk)
    autorizaciones = oc.autorizaciones.all()
    # Buscar el nivel pendiente
    pendiente = autorizaciones.filter(autorizado__isnull=True).order_by('nivel').first()
    puede_autorizar = pendiente and pendiente.responsable == request.user
    if request.method == 'POST' and puede_autorizar:
        accion = request.POST.get('accion')
        comentario = request.POST.get('comentario', '')
        pendiente.autorizado = True if accion == 'autorizar' else False
        pendiente.comentario = comentario
        pendiente.save()
        # Si fue autorizado, buscar si hay más niveles
        siguiente = oc.autorizaciones.filter(autorizado__isnull=True).order_by('nivel').first()
        if not siguiente and accion == 'autorizar':
            oc.estado = 'autorizada'
            oc.save()
        elif accion == 'autorizar':
            oc.estado = 'pendiente_autorizacion'
            oc.save()
        else:
            oc.estado = 'borrador'
            oc.save()
        messages.success(request, f'Autorización registrada: {"Autorizada" if accion=="autorizar" else "Rechazada"}.')
        return redirect('orden_compra_detail', pk=pk)
    return render(request, 'compras/orden_compra_autorizar.html', {
        'orden': oc,
        'autorizaciones': autorizaciones,
        'puede_autorizar': puede_autorizar,
        'pendiente': pendiente,
    })
from django.db.models import Avg, Q
from datetime import date

# Dashboard de compras y proveedores
@login_required
def dashboard(request):
    hoy = date.today()
    primer_dia = date(hoy.year, 1, 1)
    total_compras = OrdenCompra.objects.filter(fecha_emision__gte=primer_dia, estado__in=["enviada", "recibida_parcial", "recibida_total"]).aggregate(total=models.Sum('total'))['total'] or 0
    ordenes_pendientes = OrdenCompra.objects.exclude(estado="recibida_total").count()
    total_entregadas = OrdenCompra.objects.filter(estado="recibida_total").count()
    total_ordenes = OrdenCompra.objects.exclude(estado="borrador").count()
    cumplimiento_entregas = round((total_entregadas / total_ordenes) * 100, 2) if total_ordenes else 0
    proveedores_activos = Proveedor.objects.filter(estado="activo").count()
    # Compras por mes
    compras_meses = OrdenCompra.objects.filter(fecha_emision__year=hoy.year).values_list('fecha_emision', 'total')
    meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    compras_meses_data = [0]*12
    for fecha, total in compras_meses:
        if fecha:
            compras_meses_data[fecha.month-1] += float(total)
    # Scorecard promedio por proveedor (para gráfica)
    proveedores = Proveedor.objects.filter(estado="activo")[:10]
    proveedores_labels = [p.razon_social for p in proveedores]
    proveedores_scores = []
    from django.db.models import FloatField, F, ExpressionWrapper
    for p in proveedores:
        avg = p.scorecards.aggregate(
            score=Avg(
                ExpressionWrapper(
                    (F('calidad') + F('puntualidad') + F('cumplimiento')) / 3.0,
                    output_field=FloatField()
                )
            )
        )['score']
        proveedores_scores.append(round(avg,2) if avg else 0)

    from django.db.models import FloatField, F, ExpressionWrapper
    # Top 5 proveedores por scorecard (corrigiendo tipos)
    top_proveedores_qs = Proveedor.objects.filter(estado="activo").annotate(
        score=Avg(
            ExpressionWrapper(
                (F('scorecards__calidad') + F('scorecards__puntualidad') + F('scorecards__cumplimiento')) / 3.0,
                output_field=FloatField()
            )
        )
    ).order_by('-score')[:5]
    top_proveedores = [(p.razon_social, round(p.score,2) if p.score else 0) for p in top_proveedores_qs]

    # Distribución de estados de proveedores (para gráfica de torta)
    from django.db.models import Count
    proveedores_estado = Proveedor.objects.values('estado').annotate(total=Count('id'))
    proveedores_estado_labels = [
        dict(Proveedor._meta.get_field('estado').choices).get(e['estado'], e['estado']) for e in proveedores_estado
    ]
    proveedores_estado_data = [e['total'] for e in proveedores_estado]

    # Alertas
    alertas = []
    if ordenes_pendientes > 0:
        alertas.append(f"Hay {ordenes_pendientes} órdenes de compra pendientes de recepción.")
    if total_compras == 0:
        alertas.append("No hay compras registradas este año.")
    # Puedes agregar más alertas aquí (stock bajo, vencimientos, etc)
    context = {
        'total_compras': total_compras,
        'ordenes_pendientes': ordenes_pendientes,
        'cumplimiento_entregas': cumplimiento_entregas,
        'proveedores_activos': proveedores_activos,
        'compras_meses_labels': meses,
        'compras_meses_data': compras_meses_data,
        'proveedores_labels': proveedores_labels,
        'proveedores_scores': proveedores_scores,
        'top_proveedores': top_proveedores,
        'proveedores_estado_labels': proveedores_estado_labels,
        'proveedores_estado_data': proveedores_estado_data,
        'alertas': alertas,
    }
    return render(request, 'compras/dashboard.html', context)
from django.contrib.auth.decorators import login_required
# Exportar pedidos pendientes y compras por proveedor a CSV
@login_required
def exportar_pedidos_pendientes_csv(request):
    import csv
    proveedor_query = request.GET.get('proveedor', '').strip()
    estado_query = request.GET.get('estado', '').strip()
    pendientes = OrdenCompra.objects.select_related('proveedor').exclude(estado='recibida_total')
    if proveedor_query:
        pendientes = pendientes.filter(proveedor__razon_social__icontains=proveedor_query)
    if estado_query:
        pendientes = pendientes.filter(estado=estado_query)
    compras = OrdenCompra.objects.values('proveedor__razon_social').annotate(
        total_comprado=Sum('total'),
        num_ocs=Count('id')
    )
    if proveedor_query:
        compras = compras.filter(proveedor__razon_social__icontains=proveedor_query)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="pedidos_pendientes_y_compras.csv"'
    writer = csv.writer(response)
    writer.writerow(['--- PEDIDOS PENDIENTES ---'])
    writer.writerow(['Proveedor', 'OC', 'Fecha', 'Estado', 'Total'])
    for oc in pendientes:
        writer.writerow([
            oc.proveedor.razon_social,
            f'OC #{oc.id}',
            oc.fecha_emision,
            oc.get_estado_display(),
            oc.total
        ])
    writer.writerow([])
    writer.writerow(['--- COMPRAS POR PROVEEDOR ---'])
    writer.writerow(['Proveedor', 'Total Comprado', 'Cantidad de OCs'])
    for item in compras:
        writer.writerow([
            item['proveedor__razon_social'],
            item['total_comprado'],
            item['num_ocs']
        ])
    return response
from django.db.models import Sum, Count

# Reporte de pedidos pendientes y compras por proveedor
@login_required
def reporte_pedidos_pendientes(request):
    proveedor_query = request.GET.get('proveedor', '').strip()
    estado_query = request.GET.get('estado', '').strip()
    pendientes = OrdenCompra.objects.select_related('proveedor').exclude(estado='recibida_total')
    if proveedor_query:
        pendientes = pendientes.filter(proveedor__razon_social__icontains=proveedor_query)
    if estado_query:
        pendientes = pendientes.filter(estado=estado_query)
    compras = OrdenCompra.objects.values('proveedor__razon_social').annotate(
        total_comprado=Sum('total'),
        num_ocs=Count('id')
    )
    if proveedor_query:
        compras = compras.filter(proveedor__razon_social__icontains=proveedor_query)
    return render(request, 'compras/reporte_pedidos_pendientes.html', {
        'pendientes': pendientes.order_by('-fecha_emision'),
        'compras': compras.order_by('-total_comprado'),
    })

from django.contrib.auth.decorators import login_required
from django.db.models import Q

# Exportar historial de costos a CSV
@login_required
def exportar_historial_costos_csv(request):
    import csv
    producto_query = request.GET.get('producto', '').strip()
    proveedor_query = request.GET.get('proveedor', '').strip()
    detalles = OrdenCompraDetalle.objects.select_related('orden', 'producto', 'orden__proveedor')
    if producto_query:
        detalles = detalles.filter(Q(producto__nombre__icontains=producto_query) | Q(producto__codigo__icontains=producto_query))
    if proveedor_query:
        detalles = detalles.filter(orden__proveedor__nombre__icontains=proveedor_query)
    detalles = detalles.order_by('-orden__fecha_emision')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="historial_costos.csv"'
    writer = csv.writer(response)
    writer.writerow(['Fecha', 'Producto', 'Proveedor', 'Costo Unitario', 'Orden de Compra', 'Factura'])
    for d in detalles:
        factura = d.orden.facturas.first()
        writer.writerow([
            d.orden.fecha_emision,
            d.producto.nombre,
            d.orden.proveedor.nombre,
            d.costo_unitario,
            f'OC #{d.orden.id}',
            factura.numero_factura if factura else '',
        ])
    return response

# Reporte historial de costos por producto
@login_required
def reporte_historial_costos(request):
    producto_query = request.GET.get('producto', '').strip()
    proveedor_query = request.GET.get('proveedor', '').strip()
    detalles = OrdenCompraDetalle.objects.select_related('orden', 'producto', 'orden__proveedor')
    if producto_query:
        detalles = detalles.filter(Q(producto__nombre__icontains=producto_query) | Q(producto__codigo__icontains=producto_query))
    if proveedor_query:
        detalles = detalles.filter(orden__proveedor__nombre__icontains=proveedor_query)
    detalles = detalles.order_by('-orden__fecha_emision')
    historial = []
    for d in detalles:
        factura = d.orden.facturas.first()
        historial.append({
            'fecha': d.orden.fecha_emision,
            'producto': d.producto.nombre,
            'proveedor': d.orden.proveedor.nombre,
            'costo_unitario': d.costo_unitario,
            'orden_id': d.orden.id,
            'factura': factura.numero_factura if factura else None,
        })
    return render(request, 'compras/reporte_historial_costos.html', {'historial': historial})
from inventario.models import ProductoProveedor
# Endpoint AJAX para sugerir último costo de compra
@login_required
def sugerir_ultimo_costo(request):
    proveedor_id = request.GET.get('proveedor_id')
    producto_id = request.GET.get('producto_id')
    data = {'ultimo_costo': ''}
    if proveedor_id and producto_id:
        try:
            rel = ProductoProveedor.objects.get(proveedor_id=proveedor_id, articulo_id=producto_id)
            data['ultimo_costo'] = str(rel.ultimo_costo)
        except ProductoProveedor.DoesNotExist:
            data['ultimo_costo'] = ''
    return JsonResponse(data)
from django.http import JsonResponse
from proveedores.models import Proveedor, CondicionPago, Moneda
# Endpoint AJAX para datos del proveedor
@login_required
def proveedor_info(request):
    proveedor_id = request.GET.get('proveedor_id')
    data = {}
    try:
        proveedor = Proveedor.objects.get(pk=proveedor_id)
        data['direccion_fiscal'] = proveedor.direccion_fiscal
        data['direccion_almacen'] = proveedor.direccion_almacen
        # Condición de pago principal (la primera)
        condicion = proveedor.condiciones_pago.first()
        data['condiciones_pago'] = condicion.condicion if condicion else ''
        # Moneda principal (la primera)
        moneda = proveedor.monedas.first()
        data['moneda'] = moneda.moneda if moneda else ''
    except Proveedor.DoesNotExist:
        data = {'error': 'Proveedor no encontrado'}
    return JsonResponse(data)
import datetime
import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import SolicitudRequisicion, OrdenCompra, OrdenCompraDetalle, RecepcionMercancia, RecepcionDetalle
from .forms import SolicitudRequisicionForm, OrdenCompraForm, OrdenCompraDetalleForm, RecepcionMercanciaForm, RecepcionDetalleForm, FacturaProveedorForm
from inventario.models import Stock
from django.forms import inlineformset_factory
from django.contrib import messages

# Reporte de órdenes de compra
@login_required
def reporte_ordenes_compra(request):
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    ordenes = OrdenCompra.objects.all()
    if fecha_inicio:
        ordenes = ordenes.filter(fecha_emision__gte=fecha_inicio)
    if fecha_fin:
        ordenes = ordenes.filter(fecha_emision__lte=fecha_fin)
    return render(request, 'compras/reporte_ordenes_compra.html', {'ordenes': ordenes, 'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin})

# Exportar reporte de órdenes de compra a CSV
@login_required
def exportar_ordenes_compra_csv(request):
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    ordenes = OrdenCompra.objects.all()
    if fecha_inicio:
        ordenes = ordenes.filter(fecha_emision__gte=fecha_inicio)
    if fecha_fin:
        ordenes = ordenes.filter(fecha_emision__lte=fecha_fin)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reporte_ordenes_compra.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Proveedor', 'Fecha Emisión', 'Total', 'Estado'])
    for o in ordenes:
        writer.writerow([o.id, str(o.proveedor), o.fecha_emision, o.total, o.get_estado_display()])
    return response

# Reporte de recepciones de mercancía
@login_required
def reporte_recepciones(request):
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    recepciones = RecepcionMercancia.objects.all()
    if fecha_inicio:
        recepciones = recepciones.filter(fecha_recepcion__gte=fecha_inicio)
    if fecha_fin:
        recepciones = recepciones.filter(fecha_recepcion__lte=fecha_fin)
    return render(request, 'compras/reporte_recepciones.html', {'recepciones': recepciones, 'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin})

# Exportar reporte de recepciones a CSV
@login_required
def exportar_recepciones_csv(request):
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    recepciones = RecepcionMercancia.objects.all()
    if fecha_inicio:
        recepciones = recepciones.filter(fecha_recepcion__gte=fecha_inicio)
    if fecha_fin:
        recepciones = recepciones.filter(fecha_recepcion__lte=fecha_fin)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reporte_recepciones.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Orden', 'Fecha Recepción', 'Usuario', 'Observaciones'])
    for r in recepciones:
        writer.writerow([r.id, r.orden.id, r.fecha_recepcion, str(r.usuario), r.observaciones])
    return response
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import SolicitudRequisicion, OrdenCompra, OrdenCompraDetalle, RecepcionMercancia, RecepcionDetalle
from .forms import SolicitudRequisicionForm, OrdenCompraForm, OrdenCompraDetalleForm, RecepcionMercanciaForm, RecepcionDetalleForm, FacturaProveedorForm
from inventario.models import Stock
from inventario.models import Stock

from django.forms import inlineformset_factory
from django.contrib import messages

@login_required
def solicitud_requisicion_list(request):
    solicitudes = SolicitudRequisicion.objects.all().order_by('-fecha')
    return render(request, 'compras/solicitud_requisicion_list.html', {'solicitudes': solicitudes})

@login_required
def solicitud_requisicion_create(request):
    if request.method == 'POST':
        form = SolicitudRequisicionForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.solicitante = request.user
            obj.save()
            return redirect('solicitud_requisicion_list')
    else:
        form = SolicitudRequisicionForm()
    return render(request, 'compras/solicitud_requisicion_form.html', {'form': form})

@login_required
def solicitud_requisicion_detail(request, pk):
    solicitud = get_object_or_404(SolicitudRequisicion, pk=pk)
    return render(request, 'compras/solicitud_requisicion_detail.html', {'solicitud': solicitud})

@login_required
def solicitud_requisicion_aprobar(request, pk):
    solicitud = get_object_or_404(SolicitudRequisicion, pk=pk)
    if request.method == 'POST':
        solicitud.estado = 'aprobada'
        solicitud.gerente = request.user
        solicitud.save()
        return redirect('solicitud_requisicion_list')
    return render(request, 'compras/solicitud_requisicion_aprobar.html', {'solicitud': solicitud})

@login_required
def solicitud_requisicion_rechazar(request, pk):
    solicitud = get_object_or_404(SolicitudRequisicion, pk=pk)
    if request.method == 'POST':
        solicitud.estado = 'rechazada'
        solicitud.gerente = request.user
        solicitud.save()
        return redirect('solicitud_requisicion_list')
    return render(request, 'compras/solicitud_requisicion_rechazar.html', {'solicitud': solicitud})

# Listado de órdenes de compra
@login_required
def orden_compra_list(request):
    ordenes = OrdenCompra.objects.all().order_by('-fecha_emision')
    return render(request, 'compras/orden_compra_list.html', {'ordenes': ordenes})

# Crear nueva orden de compra (con detalles)
@login_required
def orden_compra_create(request):
    DetalleFormSet = inlineformset_factory(OrdenCompra, OrdenCompraDetalle, form=OrdenCompraDetalleForm, extra=1, can_delete=True)
    if request.method == 'POST':
        form = OrdenCompraForm(request.POST)
        formset = DetalleFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            oc = form.save()
            formset.instance = oc
            formset.save()
            messages.success(request, 'Orden de compra creada correctamente.')
            return redirect('orden_compra_list')
    else:
        form = OrdenCompraForm()
        formset = DetalleFormSet()
    return render(request, 'compras/orden_compra_form.html', {'form': form, 'formset': formset})

# Detalle de orden de compra
@login_required
def orden_compra_detail(request, pk):
    oc = get_object_or_404(OrdenCompra, pk=pk)
    autorizaciones = oc.autorizaciones.all().order_by('nivel')
    return render(request, 'compras/orden_compra_detail.html', {'orden': oc, 'autorizaciones': autorizaciones})

# Cambiar estado de la orden de compra
@login_required
def orden_compra_cambiar_estado(request, pk, nuevo_estado):
    oc = get_object_or_404(OrdenCompra, pk=pk)
    if nuevo_estado in dict(OrdenCompra.ESTADO_CHOICES):
        oc.estado = nuevo_estado
        oc.save()
        messages.success(request, f'Estado cambiado a {oc.get_estado_display()}')
    return redirect('orden_compra_detail', pk=pk)

@login_required
def recepcion_mercancia_create(request, orden_id):
    orden = get_object_or_404(OrdenCompra, pk=orden_id)
    RecepcionDetalleFormSet = inlineformset_factory(RecepcionMercancia, RecepcionDetalle, form=RecepcionDetalleForm, extra=orden.detalles.count(), can_delete=False)
    if request.method == 'POST':
        form = RecepcionMercanciaForm(request.POST)
        formset = RecepcionDetalleFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            recepcion = form.save(commit=False)
            recepcion.usuario = request.user
            recepcion.orden = orden
            recepcion.save()
            formset.instance = recepcion
            detalles = formset.save()
            # Actualizar inventario por cada producto recibido
            for detalle in detalles:
                producto = detalle.producto
                cantidad_recibida = detalle.cantidad_recibida or 0
                # Conversión de unidades: si la unidad de compra es diferente a la de consumo, usar factor de conversión
                factor = 1
                if producto.ficha_tecnica and producto.ficha_tecnica.unidad_compra != producto.ficha_tecnica.unidad_consumo:
                    factor = float(producto.ficha_tecnica.factor_conversion or 1)
                cantidad_final = float(cantidad_recibida) * factor
                # Actualiza o crea el stock físico
                stock, creado = Stock.objects.get_or_create(articulo=producto)
                stock.fisico += int(cantidad_final)
                stock.save()
            messages.success(request, 'Recepción registrada y stock actualizado correctamente.')
            return redirect('orden_compra_detail', pk=orden.id)
    else:
        form = RecepcionMercanciaForm(initial={'orden': orden})
        formset = RecepcionDetalleFormSet()
    return render(request, 'compras/recepcion_mercancia_form.html', {'form': form, 'formset': formset, 'orden': orden})

# Listar facturas de proveedor para una orden
@login_required
def factura_proveedor_list(request, orden_id):
    orden = get_object_or_404(OrdenCompra, pk=orden_id)
    facturas = orden.facturas.all()
    return render(request, 'compras/factura_proveedor_list.html', {'orden': orden, 'facturas': facturas})

# Crear factura de proveedor
@login_required
def factura_proveedor_create(request, orden_id):
    orden = get_object_or_404(OrdenCompra, pk=orden_id)
    if request.method == 'POST':
        form = FacturaProveedorForm(request.POST, request.FILES)
        if form.is_valid():
            factura = form.save(commit=False)
            factura.orden = orden
            factura.save()
            messages.success(request, 'Factura registrada correctamente.')
            return redirect('factura_proveedor_list', orden_id=orden.id)
    else:
        form = FacturaProveedorForm(initial={'orden': orden})
    return render(request, 'compras/factura_proveedor_form.html', {'form': form, 'orden': orden})

# Validar factura de proveedor
@login_required
def factura_proveedor_validar(request, factura_id):
    from .models import FacturaProveedor
    factura = get_object_or_404(FacturaProveedor, pk=factura_id)
    orden = factura.orden
    diferencia = float(factura.monto_factura) - float(orden.total)
    alerta = None
    if abs(diferencia) > 0.01 and not factura.diferencia_autorizada:
        alerta = f"¡Atención! El monto de la factura (${factura.monto_factura}) es diferente al total de la OC (${orden.total}). Autoriza la diferencia para continuar."
    if request.method == 'POST':
        if alerta and 'autorizar' in request.POST:
            factura.diferencia_autorizada = True
            factura.validada = True
            factura.save()
            messages.success(request, 'Diferencia autorizada y factura validada.')
        elif not alerta:
            factura.validada = True
            factura.save()
            messages.success(request, 'Factura validada correctamente.')
        else:
            messages.error(request, 'Debes autorizar la diferencia para validar la factura.')
        return redirect('factura_proveedor_list', orden_id=orden.id)
    return render(request, 'compras/factura_proveedor_validar.html', {'factura': factura, 'alerta': alerta, 'diferencia': diferencia, 'orden': orden})
