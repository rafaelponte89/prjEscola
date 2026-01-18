from django.shortcuts import HttpResponse, render

from aluno.utils.mensagem_http import criarMensagem

from aluno.models.ano import Ano
from aluno.services.ano import efetuar_lancamentos_fechamento_ano

# Create your views here.
def inicial_ano(request):
    return render(request,"aluno/ano/ano.html")

def gravar_ano(request):
    ano = Ano(ano=request.GET.get('ano'))
    try:
        ano.save()
        return criarMensagem("Ano salvo com sucesso","success")
    except Exception as err:
        return criarMensagem(f"Erro ao salvar ano ({err})!", "danger")

def excluir_ano(request):
    ano = Ano.objects.filter(pk=request.GET.get('ano'))[0]
    try:
        ano.delete()
        return criarMensagem("Ano deletado com sucesso", "success")
    except:
        return criarMensagem(f"Erro ao excluir ano ({ano})!","danger")

def buscar_ano(request):
    try:
        ano_recebido = request.GET.get("ano")
        if ano_recebido == "":
            ano_recebido = 0
        ano = Ano.objects.filter(ano=ano_recebido).filter()
        if ano:
             return render(request, 'aluno/ano/partials/listar_anos.html', {
                    'anos': ano,
             })
        else:
            return criarMensagem("Nenhum resultado!","info")

    except Exception as err:
        print(err)
        return criarMensagem("Algum erro aconteceu!","danger")
    
def listar_ano(request):
    anos = Ano.objects.all().order_by('-ano')[:10]
    return render(request, 'aluno/ano/partials/listar_anos.html', {
        'anos': anos,
    })

def fechar_abrir_ano(request):
    ano = Ano.objects.get(pk=request.GET.get('ano'))
    ano.fechado = not ano.fechado
    ano.save()
    efetuar_lancamentos_fechamento_ano(ano)

    return HttpResponse(ano.fechado)
    
def status_ano(request):
    ano = Ano.objects.get(pk=request.GET.get('ano'))
    return HttpResponse(ano.fechado)

def selecionar_ano(request):
    ano = Ano.objects.filter(ano=request.GET.get('ano')).first()
    return HttpResponse(ano.id)
   



