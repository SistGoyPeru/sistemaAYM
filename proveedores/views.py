import openpyxl
from openpyxl.utils import get_column_letter
from django.http import HttpResponse
def exportar_proveedor_excel(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    scorecards = proveedor.scorecards.all().order_by('-fecha')
    incidentes = proveedor.incidentes.all().order_by('-fecha')
    ordenes = proveedor.ordenes_compra.all().order_by('-fecha')
    facturas = proveedor.facturas.all().order_by('-fecha')
    devoluciones = proveedor.devoluciones.all().order_by('-fecha')

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Proveedor"

    ws.append(["Reporte de Proveedor"])
    ws.append(["Razón Social", proveedor.razon_social])
    ws.append(["Nombre Comercial", proveedor.nombre_comercial])
    ws.append(["ID Fiscal", proveedor.id_fiscal])
    ws.append(["Teléfono", proveedor.telefono])
    ws.append(["Email", proveedor.email])
    ws.append(["Estado", proveedor.get_estado_display()])
    ws.append([])

    ws.append(["Scorecard"])
    ws.append(["Fecha", "Calidad", "Puntualidad", "Cumplimiento"])
    for s in scorecards:
        ws.append([s.fecha, s.calidad, s.puntualidad, s.cumplimiento])
    ws.append([])

    ws.append(["Incidentes"])
    ws.append(["Fecha", "Descripción"])
    for i in incidentes:
        ws.append([i.fecha, i.descripcion])
    ws.append([])

    ws.append(["Órdenes de Compra"])
    ws.append(["Código", "Estado", "Fecha"])
    for o in ordenes:
        ws.append([o.codigo, o.get_estado_display(), o.fecha])
    ws.append([])

    ws.append(["Facturas"])
    ws.append(["Número", "Estado", "Fecha", "Monto"])
    for f in facturas:
        ws.append([f.numero, f.get_estado_display(), f.fecha, f.monto])
    ws.append([])

    ws.append(["Devoluciones"])
    ws.append(["Fecha", "Motivo", "Nota de Crédito"])
    for d in devoluciones:
        ws.append([d.fecha, d.motivo, d.nota_credito])

    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        ws.column_dimensions[column].width = max_length + 2

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="proveedor_{proveedor.pk}.xlsx"'
    wb.save(response)
    return response
def detalle_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    scorecards = proveedor.scorecards.all().order_by('-fecha')
    incidentes = proveedor.incidentes.all().order_by('-fecha')
    # Calcular promedios
    if scorecards.exists():
        avg_calidad = round(sum(s.calidad for s in scorecards) / scorecards.count(), 2)
        avg_puntualidad = round(sum(s.puntualidad for s in scorecards) / scorecards.count(), 2)
        avg_cumplimiento = round(sum(s.cumplimiento for s in scorecards) / scorecards.count(), 2)
    else:
        avg_calidad = avg_puntualidad = avg_cumplimiento = None
    ordenes = proveedor.ordenes_compra.all().order_by('-fecha')
    facturas = proveedor.facturas.all().order_by('-fecha')
    devoluciones = proveedor.devoluciones.all().order_by('-fecha')
    return render(request, 'proveedores/detalle.html', {
        'proveedor': proveedor,
        'scorecards': scorecards,
        'incidentes': incidentes,
        'avg_calidad': avg_calidad,
        'avg_puntualidad': avg_puntualidad,
        'avg_cumplimiento': avg_cumplimiento,
        'ordenes': ordenes,
        'facturas': facturas,
        'devoluciones': devoluciones,
    })
from .models import ProductoProveedor
def catalogo_productos(request):
    productos = ProductoProveedor.objects.all()
    return render(request, 'proveedores/catalogo.html', {'productos': productos})

from django.shortcuts import render, get_object_or_404, redirect
from .models import Proveedor
from .forms import ProveedorForm, DatosBancariosFormSet, CondicionPagoFormSet, DocumentoLegalFormSet, MonedaFormSet, ProductoProveedorFormSet, IncidenteProveedorFormSet

def lista_proveedores(request):
    proveedores = Proveedor.objects.all()
    total = proveedores.count()
    activos = proveedores.filter(estado="activo").count()
    en_prueba = proveedores.filter(estado="en_prueba").count()
    bloqueados = proveedores.filter(estado="bloqueado").count()
    return render(request, 'proveedores/lista.html', {
        'proveedores': proveedores,
        'total': total,
        'activos': activos,
        'en_prueba': en_prueba,
        'bloqueados': bloqueados,
    })

def nuevo_proveedor(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        proveedor = None
        if form.is_valid():
            proveedor = form.save(commit=False)
        bancos_formset = DatosBancariosFormSet(request.POST, request.FILES, instance=proveedor)
        pago_formset = CondicionPagoFormSet(request.POST, instance=proveedor)
        doc_formset = DocumentoLegalFormSet(request.POST, request.FILES, instance=proveedor)
        moneda_formset = MonedaFormSet(request.POST, instance=proveedor)
        productos_formset = ProductoProveedorFormSet(request.POST, instance=proveedor)
        incidente_formset = IncidenteProveedorFormSet(request.POST, instance=proveedor)
        if form.is_valid() and bancos_formset.is_valid() and pago_formset.is_valid() and doc_formset.is_valid() and moneda_formset.is_valid() and productos_formset.is_valid() and incidente_formset.is_valid():
            proveedor.save()
            bancos_formset.instance = proveedor
            pago_formset.instance = proveedor
            doc_formset.instance = proveedor
            moneda_formset.instance = proveedor
            productos_formset.instance = proveedor
            incidente_formset.instance = proveedor
            bancos_formset.save()
            pago_formset.save()
            doc_formset.save()
            moneda_formset.save()
            productos_formset.save()
            incidente_formset.save()
            return redirect('lista_proveedores')
    else:
        form = ProveedorForm()
        bancos_formset = DatosBancariosFormSet(instance=None)
        pago_formset = CondicionPagoFormSet(instance=None)
        doc_formset = DocumentoLegalFormSet(instance=None)
        moneda_formset = MonedaFormSet(instance=None)
        productos_formset = ProductoProveedorFormSet(instance=None)
        incidente_formset = IncidenteProveedorFormSet(instance=None)
    return render(request, 'proveedores/form.html', {
        'form': form,
        'bancos_formset': bancos_formset,
        'pago_formset': pago_formset,
        'doc_formset': doc_formset,
        'moneda_formset': moneda_formset,
        'productos_formset': productos_formset,
        'incidente_formset': incidente_formset,
    })


def editar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        bancos_formset = DatosBancariosFormSet(request.POST, request.FILES, instance=proveedor)
        pago_formset = CondicionPagoFormSet(request.POST, instance=proveedor)
        doc_formset = DocumentoLegalFormSet(request.POST, request.FILES, instance=proveedor)
        moneda_formset = MonedaFormSet(request.POST, instance=proveedor)
        productos_formset = ProductoProveedorFormSet(request.POST, instance=proveedor)
        incidente_formset = IncidenteProveedorFormSet(request.POST, instance=proveedor)
        if form.is_valid() and bancos_formset.is_valid() and pago_formset.is_valid() and doc_formset.is_valid() and moneda_formset.is_valid() and productos_formset.is_valid() and incidente_formset.is_valid():
            form.save()
            bancos_formset.save()
            pago_formset.save()
            doc_formset.save()
            moneda_formset.save()
            productos_formset.save()
            incidente_formset.save()
            return redirect('lista_proveedores')
    else:
        form = ProveedorForm(instance=proveedor)
        bancos_formset = DatosBancariosFormSet(instance=proveedor)
        pago_formset = CondicionPagoFormSet(instance=proveedor)
        doc_formset = DocumentoLegalFormSet(instance=proveedor)
        moneda_formset = MonedaFormSet(instance=proveedor)
        productos_formset = ProductoProveedorFormSet(instance=proveedor)
        incidente_formset = IncidenteProveedorFormSet(instance=proveedor)
    return render(request, 'proveedores/form.html', {
        'form': form,
        'proveedor': proveedor,
        'bancos_formset': bancos_formset,
        'pago_formset': pago_formset,
        'doc_formset': doc_formset,
        'moneda_formset': moneda_formset,
        'productos_formset': productos_formset,
        'incidente_formset': incidente_formset,
    })

def eliminar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        proveedor.delete()
        return redirect('lista_proveedores')
    return render(request, 'proveedores/eliminar.html', {'proveedor': proveedor})
