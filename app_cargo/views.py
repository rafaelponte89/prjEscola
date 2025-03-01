from django.shortcuts import render, redirect
from .models import Cargos
from .forms import formularioCargo
from django.contrib import messages
# Create your views here.

def cargos(request):
    cargos = Cargos.objects.all()
    if request.method == 'POST':
        form = formularioCargo(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listarcargos')
    else:
        form = formularioCargo()
    return render(request,'cadastrar_cargo.html',{'form':form, 'cargos':cargos})

def atualizar_cargos(request, cargo_id):
    cargos = Cargos.objects.all()
    cargo = Cargos.objects.get(pk=cargo_id)

    if request.method == 'POST':
        form = formularioCargo(request.POST, instance=cargo)
        if form.is_valid():
            form.save()
            messages.success(request,"Cargo atualizado!")

            return redirect('listarcargos')
    else:
        form = formularioCargo(instance=cargo)

    
    return render(request,'cadastrar_cargo.html',{'form':form, 'cargos':cargos})





