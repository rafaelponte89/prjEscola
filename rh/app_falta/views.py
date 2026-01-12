from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.core.paginator import Paginator
from .forms import formularioTF
from .models import Faltas

# Create your views here.

# listar e incluir faltas
def faltas(request):
    faltas_queryset = Faltas.objects.all().order_by('descricao')
    paginator = Paginator(faltas_queryset, 5)
    page_number = request.GET.get('page')
    faltas = paginator.get_page(page_number)
    
    if request.method == 'POST':
        form = formularioTF(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listarfaltas')
    else:
        form = formularioTF()
    return render(request,'app_falta/cadastrar_tipo_falta.html',{'form':form, 'faltas':faltas})

def atualizar_faltas(request, falta_id):
    
    falta = Faltas.objects.get(pk=falta_id)
    faltas_queryset = Faltas.objects.all().order_by('descricao')
    paginator = Paginator(faltas_queryset, 5)
    page_number = request.GET.get('page')
    faltas = paginator.get_page(page_number)
    
    if request.method == 'POST':
        form = formularioTF(request.POST, instance=falta)
        if form.is_valid():
            form.save()
            messages.success(request,"Falta atualizada!")

            return redirect(f"{reverse('listarfaltas')}?page={page_number}") 
    else:
        form = formularioTF(instance=falta)

    
    return render(request,'app_falta/cadastrar_tipo_falta.html',{'form':form, 'faltas':faltas})