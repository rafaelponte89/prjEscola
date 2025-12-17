from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import formularioTF
from .models import Faltas

# Create your views here.

# listar e incluir faltas
def faltas(request):
    faltas = Faltas.objects.all()
    if request.method == 'POST':
        form = formularioTF(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listarfaltas')
    else:
        form = formularioTF()
    return render(request,'app_falta/cadastrar_tipo_falta.html',{'form':form, 'faltas':faltas})

def atualizar_faltas(request, falta_id):
    faltas = Faltas.objects.all()
    falta = Faltas.objects.get(pk=falta_id)
    
    if request.method == 'POST':
        form = formularioTF(request.POST, instance=falta)
        if form.is_valid():
            form.save()
            messages.success(request,"Falta atualizada!")

            return redirect('listarfaltas')
    else:
        form = formularioTF(instance=falta)

    
    return render(request,'app_falta/cadastrar_tipo_falta.html',{'form':form, 'faltas':faltas})