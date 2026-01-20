from django.shortcuts import render, redirect
from rh.models.pontuacao import Pontuacoes
from rh.models.pessoa import Pessoas
from rh.forms.pontuacao import formularioPontuacao
from django.contrib import messages

from django.core.paginator import Paginator

from rh.services.pessoa import verificar_ano_saida
    
def atualizar_pontuacoes(request, pontuacao_id, pessoa_id):

    pontuacao = Pontuacoes.objects.get(pk=pontuacao_id)
    pontuacoes = Pontuacoes.objects.filter(pessoa=pessoa_id)
    pessoa = Pessoas.objects.get(pk=pessoa_id)

    if request.method == 'POST':
        form = formularioPontuacao(request.POST, instance=pontuacao)
        
        if form.is_valid():
           
            form.save()
            
            messages.success(request,"Pontuação Gravada!")
            return redirect('lancarpontuacao',pessoa_id)
        else:
            messages.error(request,"Erro ao  Gravar Pontuação!",'danger')
            

    else:
        form = formularioPontuacao(instance=pontuacao,initial={'pessoa':pessoa})
    
    return render(request,'rh/pontuacao/lancar_pontuacao.html',{'form':form,'pessoa':pessoa,'pontuacoes':pontuacoes})



def excluir_pontuacoes(request, pessoa_id, pontuacao_id):
    pontuacao = Pontuacoes.objects.get(pk=pontuacao_id)
    pontuacoes = Pontuacoes.objects.filter(pessoa=pessoa_id).order_by('ano')
    pessoa = Pessoas.objects.get(pk=pessoa_id)

    if request.method == 'GET':
        pontuacao.delete()    
        messages.success(request,"Pontuação Apagada!")
        return redirect('lancarpontuacao',pessoa_id)     
    else:
        form = formularioPontuacao(initial={'pessoa':pessoa})
    
    return render(request,'rh/pontuacao/lancar_pontuacao.html',{'form':form,'pessoa':pessoa,'pontuacoes':pontuacoes})

def lancar_pontuacoes(request, pessoa_id):

    pessoa = Pessoas.objects.get(pk=pessoa_id)
    pontuacoes_queryset = Pontuacoes.objects.filter(pessoa=pessoa_id).order_by('-ano')
    paginator = Paginator(pontuacoes_queryset, 5)
    page_number = request.GET.get('page')
    pontuacoes = paginator.get_page(page_number)
    
    ativo = verificar_ano_saida(pessoa_id)
    if request.method == 'POST':
        form = formularioPontuacao(request.POST)
        ano = form['ano'].value()
        if pessoa.admissao.year <= int(ano) and ativo :
            if form.is_valid():
            
                form.save()
                messages.success(request,"Pontuação Gravada!")
                return redirect('lancarpontuacao',pessoa_id)
            else:
                messages.error(request,"Erro ao  Gravar Pontuação!",'danger')
        else:
            if pessoa.saida == None:
                messages.error(request,f"Erro ao  Gravar Pontuação! Ano Admissao: {pessoa.admissao.year}",'danger')

            else:
                messages.error(request,f"Erro ao  Gravar Pontuação! Ano Admissao: {pessoa.admissao.year} Ano Saída: {pessoa.saida.year}",'danger')


    else:
        form = formularioPontuacao(initial={'pessoa':pessoa})
        
    
    return render(request,'rh/pontuacao/lancar_pontuacao.html',{'form':form,'pessoa':pessoa,'pontuacoes':pontuacoes})



