from django.shortcuts import HttpResponse, render

from aluno.models.aluno import Aluno
from aluno.models.matricula import Matricula
from utilitarios.utilitarios import criarMensagem

from aluno.models.ano import Ano
from aluno.services.ano import retornarStatusAno, efetuar_lancamentos_fechamento_ano


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
        ano = Ano.objects.filter(ano=ano_recebido)
        if ano:
        
            return HttpResponse(f"""<tr><td class='text-center'> <button type='button' class='btn btn-outline-dark btn-lg selecionarAno'
                 value={ano[0].ano} > {ano[0].ano} </button></td>
                  <td class='text-center'><button type='button' class='btn btn-outline-dark btn-lg status'
                 value={ano[0].id} > 
                          {retornarStatusAno(ano[0].id)}
                        </button></td></td>
                 <td class='text-center'> <button type='button' class='btn btn-outline-dark btn-lg excluir'
                 value={ano[0].id} > 
                          <i class="bi bi-trash3-fill"></i>
                        </button></td>
                
                </tr>""")
        else:
            return criarMensagem("Nenhum resultado!","info")

    except:
        return criarMensagem("Algum erro aconteceu!","danger")
    

def listar_ano(request):
    anos = Ano.objects.all()[:10]
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
   



