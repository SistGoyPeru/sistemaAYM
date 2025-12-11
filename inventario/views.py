from django.shortcuts import render, get_object_or_404, redirect
from .models import Articulo, Familia
from .forms import ArticuloForm, FamiliaForm, FichaTecnicaForm, StockForm

def lista_articulos(request):
    articulos = Articulo.objects.select_related('familia').all()
    return render(request, 'inventario/lista_articulos.html', {'articulos': articulos})

def nuevo_articulo(request):
    ficha_form = FichaTecnicaForm(request.POST or None, request.FILES or None, prefix='ficha')
    stock_form = StockForm(request.POST or None, prefix='stock')
    if request.method == 'POST':
        form = ArticuloForm(request.POST)
        if form.is_valid() and ficha_form.is_valid() and stock_form.is_valid():
            ficha = ficha_form.save()
            articulo = form.save(commit=False)
            articulo.ficha_tecnica = ficha
            articulo.save()
            stock = stock_form.save(commit=False)
            stock.articulo = articulo
            stock.save()
            return redirect('lista_articulos')
    else:
        form = ArticuloForm()
    return render(request, 'inventario/form_articulo.html', {'form': form, 'ficha_form': ficha_form, 'stock_form': stock_form})

def editar_articulo(request, pk):
    articulo = get_object_or_404(Articulo, pk=pk)
    ficha = articulo.ficha_tecnica if articulo.ficha_tecnica else None
    ficha_form = FichaTecnicaForm(request.POST or None, request.FILES or None, instance=ficha, prefix='ficha')
    stock = articulo.stock if hasattr(articulo, 'stock') else None
    stock_form = StockForm(request.POST or None, instance=stock, prefix='stock')
    if request.method == 'POST':
        form = ArticuloForm(request.POST, instance=articulo)
        if form.is_valid() and ficha_form.is_valid() and stock_form.is_valid():
            ficha = ficha_form.save()
            articulo = form.save(commit=False)
            articulo.ficha_tecnica = ficha
            articulo.save()
            stock = stock_form.save(commit=False)
            stock.articulo = articulo
            stock.save()
            return redirect('lista_articulos')
    else:
        form = ArticuloForm(instance=articulo)
    return render(request, 'inventario/form_articulo.html', {'form': form, 'ficha_form': ficha_form, 'stock_form': stock_form, 'articulo': articulo})

def eliminar_articulo(request, pk):
    articulo = get_object_or_404(Articulo, pk=pk)
    if request.method == 'POST':
        articulo.delete()
        return redirect('lista_articulos')
    return render(request, 'inventario/confirmar_eliminar_articulo.html', {'articulo': articulo})

def lista_familias(request):
    familias = Familia.objects.all()
    return render(request, 'inventario/lista_familias.html', {'familias': familias})

def nueva_familia(request):
    if request.method == 'POST':
        form = FamiliaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_familias')
    else:
        form = FamiliaForm()
    return render(request, 'inventario/form_familia.html', {'form': form})

def editar_familia(request, pk):
    familia = get_object_or_404(Familia, pk=pk)
    if request.method == 'POST':
        form = FamiliaForm(request.POST, instance=familia)
        if form.is_valid():
            form.save()
            return redirect('lista_familias')
    else:
        form = FamiliaForm(instance=familia)
    return render(request, 'inventario/form_familia.html', {'form': form, 'familia': familia})

def eliminar_familia(request, pk):
    familia = get_object_or_404(Familia, pk=pk)
    if request.method == 'POST':
        familia.delete()
        return redirect('lista_familias')
    return render(request, 'inventario/confirmar_eliminar_familia.html', {'familia': familia})
