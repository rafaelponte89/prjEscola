from django.shortcuts import render, redirect
from .models import Pontuacoes
from app_pessoa.models import Pessoas
from .forms import formularioPontuacao
from django.contrib import messages

from .pontuacoes import criar_salvar_pontuacao, deletar_pontuacao_ano

def verificar_ano_saida(pessoa_id):
    pessoa = Pessoas.objects.get(pk=pessoa_id)
   
    ativo = pessoa.saida 
    if ativo is not None:
        ano = pessoa.admissao.year
        if ano >= ativo.year:
            return True
        else:
            return False
    else:
        return True
    
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
    
    return render(request,'app_pontuacao/lancar_pontuacao.html',{'form':form,'pessoa':pessoa,'pontuacoes':pontuacoes})



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
    
    return render(request,'app_pontuacao/lancar_pontuacao.html',{'form':form,'pessoa':pessoa,'pontuacoes':pontuacoes})

def lancar_pontuacoes(request, pessoa_id):

    pessoa = Pessoas.objects.get(pk=pessoa_id)
    pontuacoes = Pontuacoes.objects.filter(pessoa=pessoa_id).order_by('ano')
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
        
    
    return render(request,'app_pontuacao/lancar_pontuacao.html',{'form':form,'pessoa':pessoa,'pontuacoes':pontuacoes})



