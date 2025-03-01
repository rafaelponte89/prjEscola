from django.shortcuts import render, HttpResponse
from .models import Instituicao
from django.views.decorators.csrf import csrf_exempt
from utilitarios.utilitarios import criarMensagem

# Create your views here.

def instituicao(request):
    return render(request, 'instituicao.html')

@csrf_exempt
def gravar_instituicao(request):
    try:
        nome_instituicao = request.POST.get('instituicao')
        instituicao = Instituicao()
        instituicao.instituicao = nome_instituicao.upper()
        instituicao.save()

        return criarMensagem('Instituição salva com sucesso!','success')
    except:
        return criarMensagem('Erro ao gravar Instituição!','danger')

@csrf_exempt
def excluir_instituicao(request):
    try:
        instituicao_id = request.POST.get('instituicao')
        instituicao = Instituicao.objects.get(pk=instituicao_id)
        instituicao.delete()
        return criarMensagem('Instituição deletada com sucesso!!','success')


    except Exception as erro:
        return criarMensagem(f'Erro ao excluir instituição!{erro}','danger')
    
def retornar_tabela_instituicao(instituicao):
    linha = ''
    for i in instituicao:
        linha += f"""<tr> <td>{i.instituicao}</td> 
                            <td class='text-center'> <button type='button' class='btn btn-outline-dark btn-lg atualizar'
                            value={i.id} > 
                          <i class="bi bi-arrow-repeat"></i>
                            <td class='text-center'> <button type='button' class='btn btn-outline-dark btn-lg excluir'
                            value={i.id} > 
                          <i class="bi bi-trash3-fill"></i>
                        </button></td>
                        </tr>"""
    return linha

@csrf_exempt
def carregar_instituicoes(request):
    instituicoes = Instituicao.objects.all().order_by('instituicao')[:10]
    tabela = ''
    tabela = retornar_tabela_instituicao(instituicoes)
    return HttpResponse(tabela)

@csrf_exempt
def pesquisar_instituicao(request):
    try:
        instituicao_nome = request.POST.get('instituicao')
        print(instituicao_nome)
        instituicoes = Instituicao.objects.filter(instituicao__icontains=instituicao_nome)

        if instituicoes:
            tabela = retornar_tabela_instituicao(instituicoes)
            return HttpResponse(tabela)
        else:
            return criarMensagem('Nenhuma instituição encontrada!','info')
    except Exception as err:
        return criarMensagem(f'Erro ao pesquisar! {err}','danger')