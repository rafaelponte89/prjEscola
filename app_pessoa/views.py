from django.shortcuts import render, redirect, HttpResponse
from .models import Pessoas
from .forms import formularioPessoa
from django.contrib import messages

# Create your views here.
# atualiza informações de uma pessoa
def atualizar_pessoa(request, pessoa_id):
    pessoa = Pessoas.objects.get(pk=pessoa_id)
    
    if request.method == 'POST':
        form = formularioPessoa(request.POST, instance=pessoa)
        
        if form.is_valid():
            
            form.save()
            messages.success(request,"Pessoa atualizada!")
            return redirect('atualizarpessoa', form.cleaned_data['id'])
    else:
        form = formularioPessoa(instance=pessoa)
    return render(request,'app_pessoa/cadastrar_pessoas.html',{'form':form,'pessoa':pessoa})

# listar e incluir pessoas
def cadastrar_pessoas(request):
    pessoas = Pessoas.objects.all()
    
    
    if request.method == 'POST':
        form = formularioPessoa(request.POST)
    
        if form.is_valid():
            form.save()
            messages.success(request,"Pessoa registrada!")
            return redirect('cadastrarpessoas')
    else:

        form = formularioPessoa()
    return render(request,'app_pessoa/cadastrar_pessoas.html',{'form':form, 'pessoas':pessoas})


def tela_pesquisar_pessoas(request):

    return render(request,"app_pessoa/pesquisar_pessoas.html")

def selecionar_pessoa(request):
    matricula = request.GET.get('matricula')
    pessoa = Pessoas.objects.get(pk=matricula)

    return HttpResponse(f'<button class="btn btn-dark mr-1" id="matpes" value="{matricula}"> {matricula} </button> | ' + pessoa.nome + ' | ')

def pesquisar_pessoas(request):

    nome = request.GET.get('nome')
    pessoas = ''
    #<!-- <td><a class='btn btn-info' href="{% url 'listarficha' pessoa.id %}"><span class="material-icons">
    #            visibility
    #            </span></a></td>
    #        <td><a class='btn btn-info' href="{% url 'lancarfalta' pessoa.id %}"><span class="material-icons">
    #            add
    #            </span></a> </td> -->
    
    pessoas = Pessoas.objects.filter(nome__contains=nome).order_by('nome')[:10]
    corpo = ""
    for pessoa in pessoas:
        corpo += f"""
       
        <tr>
        <td class="text-center align-middle">{pessoa.id}</td>

         <td class="text-left align-middle">{pessoa.nome}</td>
         <td class="text-center align-middle">{pessoa.cargo}</td>

            <td>
                <button class='btn btn-info selpes' value="{pessoa.id}"><span class="material-icons">
                        check_circle
                    </span></button>

            </td>
           
        </tr>"""

    return HttpResponse(corpo)
