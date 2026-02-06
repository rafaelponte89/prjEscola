from django.contrib import messages
from django.shortcuts import HttpResponse, redirect, render
from django.template.loader import render_to_string

from rh.forms.pessoa import FormularioPessoa
from rh.models.pessoa import Pessoas


# Create your views here.
# atualiza informações de uma pessoa
def atualizar_pessoa(request, pessoa_id):
    pessoa = Pessoas.objects.get(pk=pessoa_id)
    
    if request.method == 'POST':
        form = FormularioPessoa(request.POST, instance=pessoa)
        
        if form.is_valid():
            
            form.save()
            messages.success(request,"Pessoa atualizada!")
            return redirect('atualizarpessoa', form.cleaned_data['id'])
    else:
        form = FormularioPessoa(instance=pessoa)
    return render(request,'rh/pessoa/cadastrar_pessoas.html',{'form':form,'pessoa':pessoa})

from django.contrib.auth.decorators import login_required, permission_required


def cadastrar_pessoas(request):
    pessoas = Pessoas.objects.all()
    
    
    if request.method == 'POST':
        form = FormularioPessoa(request.POST)
    
        if form.is_valid():
            form.save()
            messages.success(request,"Pessoa registrada!")
            return redirect('cadastrarpessoas')
    else:

        form = FormularioPessoa()
    return render(request,'rh/pessoa/cadastrar_pessoas.html',{'form':form, 'pessoas':pessoas})


def tela_pesquisar_pessoas(request):

    return render(request,"rh/pessoa/pesquisar_pessoas.html")

def selecionar_pessoa(request):
    matricula = request.GET.get('matricula')
    pessoa = Pessoas.objects.get(pk=matricula)

    return HttpResponse(f'<button class="btn btn-dark mr-1" id="matpes" value="{matricula}"> {matricula} </button> | ' + pessoa.nome + ' | ')

def pesquisar_pessoas(request):
    nome = request.GET.get('nome', '').strip()

    if not nome or len(nome) < 2:
        return HttpResponse("")

    pessoas = (
        Pessoas.objects
        .filter(nome__icontains=nome)
        .order_by('nome')[:10]
    )

    html = ""
    for pessoa in pessoas:
        html += render_to_string(
            "rh/pessoa/partials/linha_pessoa.html",
            {"pessoa": pessoa},
            request=request
        )

    return HttpResponse(html)
