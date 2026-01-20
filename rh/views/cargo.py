from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse

from rh.forms.cargo import formularioCargo
from rh.models.cargo import Cargos

from django.core.paginator import Paginator
# Create your views here.

def cargos(request):
    cargos_queryset = Cargos.objects.all().order_by('cargo')
    paginator = Paginator(cargos_queryset, 5)
    page_number =request.GET.get('page')
    cargos = paginator.get_page(page_number)
    
    if request.method == 'POST':
        form = formularioCargo(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listarcargos')
    else:
        form = formularioCargo()
    return render(request,'rh/cargo/cadastrar_cargo.html',{'form':form, 'cargos':cargos})

def atualizar_cargos(request, cargo_id):
    cargos_queryset = Cargos.objects.all().order_by('cargo')
    paginator = Paginator(cargos_queryset, 5)

    page_number =request.GET.get('page')
    cargos = paginator.get_page(page_number)

    cargo = Cargos.objects.get(pk=cargo_id)

    if request.method == 'POST':
        form = formularioCargo(request.POST, instance=cargo)
        if form.is_valid():
            form.save()
            messages.success(request,"Cargo atualizado!")
            
            return redirect(f"{reverse('listarcargos')}?page={page_number}")
    else:
        form = formularioCargo(instance=cargo)

    
    return render(request,'rh/cargo/cadastrar_cargo.html',{'form':form, 'cargos':cargos})





