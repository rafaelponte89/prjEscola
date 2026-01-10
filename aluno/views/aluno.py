
from django.http import HttpResponse
from django.shortcuts import render
import io

from aluno.models.classe import Classe
from aluno.models.matricula import Matricula
from aluno.utils.texto import  padronizar_nome

from aluno.forms.aluno import FrmAluno, FrmAlunoUpdate
from aluno.models.aluno import Aluno
from django.shortcuts import get_object_or_404

from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from aluno.forms.telefone import TelefoneFormSet

from django.db import transaction


REF_TAMANHO_NOME = 2
REF_TAMANHO_RA = 7
EMAIL = "victorianonino@educa.orlandia.sp.gov.br"
from aluno.services.aluno import buscar_duplicados, renderizarTabela, pesquisar_alunos_por_nome
from aluno.services.mensagem import criarMensagemJson


def index(request):
    if request.method == "POST":
        # Se o formulário de cadastro de aluno foi enviado
        return salvar_aluno(request)
    # Se for GET, apenas renderiza o formulário
    form = FrmAluno()
    return render(request, "aluno/aluno/index.html", {"form": form})

# Gravar registro do Aluno
def salvar_aluno(request):
    nome = padronizar_nome(request.POST.get("nome"))
    ra = request.POST.get("ra")

    form = FrmAluno({"nome": nome, "ra": ra})

    # Validação RA duplicado
    if Aluno.objects.filter(ra=ra).exists():
        return JsonResponse({
            'success': False,
            'mensagem': criarMensagemJson(f'Já existe RA {ra} cadastrado para outro aluno!','danger')
        })

    if not form.is_valid():
        return JsonResponse({
            'success': False,
            'mensagem': criarMensagemJson(f'Dados Inválidos!','danger')
        })

    if len(nome) <= REF_TAMANHO_NOME:
        return JsonResponse({
            'success': False,
            'mensagem': criarMensagemJson(f'Nome muito Pequeno!','warning')
        })

    if len(ra) <= REF_TAMANHO_RA:
        return JsonResponse({
            'success': False,
            'mensagem': criarMensagemJson(f'RA muito Pequeno!','warning')
        })

    # Salva aluno
    form.save()

    alunos = Aluno.retornarNUltimos()
    nomes_duplicados = buscar_duplicados(alunos)
    html = renderizarTabela(alunos, nomes_duplicados, request)

    return JsonResponse({
        'success': True,
        'mensagem': criarMensagemJson(f'Aluno Registrado com Sucesso!','success'),
        'html': html
    })


@transaction.atomic
def atualizar_aluno(request):
    aluno = get_object_or_404(Aluno, rm=request.POST.get("rm"))

    form = FrmAlunoUpdate(request.POST, instance=aluno)
    formset = TelefoneFormSet(request.POST, instance=aluno)

    if form.is_valid() and formset.is_valid():
        form.save()
        formset.save()

        return JsonResponse({
            'success': True,
            'mensagem': criarMensagemJson(
                'Aluno atualizado com sucesso!!!',
                'success'
            )
        })

    return JsonResponse({
        'success': False,
        'html': render_to_string(
            'aluno/aluno/partials/form_update.html',
            {
                'form': form,
                'formset': formset,
                'aluno': aluno
            },
            request=request
        )
    })
        
def pesquisar_aluno(request):
    nome = padronizar_nome(request.POST.get("nome", ""))
    filtro = request.POST.get("filtro")

    if len(nome) <= REF_TAMANHO_NOME:
        # Últimos 5 registros
        alunos = Aluno.retornarNUltimos().prefetch_related('telefones')
        nomes_duplicados = buscar_duplicados(alunos)
        html = renderizarTabela(alunos, nomes_duplicados, request)
        return JsonResponse({'html': html, 'mensagem': ''})  # sem mensagem

    alunos = pesquisar_alunos_por_nome(nome, filtro).prefetch_related('telefones')
    nomes_duplicados = buscar_duplicados(alunos)
    html = renderizarTabela(alunos, nomes_duplicados, request)

    if not alunos:
       
        return JsonResponse({'html': '', 'mensagem': criarMensagemJson('Aluno não Encontrado!','info')})
    
    return JsonResponse({'html': html, 'mensagem': ''})
        
def cancelarRM(request):
    rm = request.POST.get("rm")
    try:
        aluno = Aluno.objects.get(rm=rm)
    except Aluno.DoesNotExist:
        return JsonResponse({"success": False, "mensagem":criarMensagemJson('Aluno não Encontrado!', 'info')})

    # Defina explicitamente o status de cancelado
    aluno.status = Aluno.STATUS_CANCELADO
    aluno.save()

    return JsonResponse({"success": False, "mensagem":criarMensagemJson(f'Aluno {aluno.nome}, RM {aluno.rm} Cancelado com Sucesso!', 'success')})
 
def recarregarTabela(request):
    alunos = Aluno.retornarNUltimos().prefetch_related('telefones')
    nomes_duplicados = buscar_duplicados(alunos)
    html = renderizarTabela(alunos, nomes_duplicados, request)
  
    return JsonResponse({'html': html, 'mensagem': ''})  # sem mensagem

def buscar_dados_aluno(request):
    aluno = get_object_or_404(Aluno, rm=request.POST.get("rm"))

    form = FrmAlunoUpdate(instance=aluno)
    formset = TelefoneFormSet(instance=aluno)

    return render(
        request,
        "aluno/aluno/partials/form_update.html",
        {
            "form": form,
            "formset": formset,
            "aluno": aluno,
        }
    )

def buscarRMCancelar(request):
    rm = request.POST.get('rm')
    aluno = Aluno.objects.values('rm', 'nome').get(pk=rm)
    return JsonResponse({"rm": aluno['rm'], "nome": aluno['nome']})

   
# em desenvolvimento 10/05/2024
def buscar_historico_matriculas(request):
    rm = request.POST.get('rm')
    aluno = Aluno.objects.get(pk=rm)
    matriculas_aluno = Matricula.objects.filter(aluno=aluno)
    dados_matricula=''
    
    for matricula in matriculas_aluno:
        descritivo_situacao = Matricula.retornarDescricaoSituacao(matricula)
        dados_matricula += f"""
                   <div class="col-12 form-group d-flex align-items-center"> 
                  <input        
                    type="text"     
                    class="form-control m-2" 
                    title="Início: {(matricula.data_matricula).strftime("%d/%m/%Y")} || Fim: { (matricula.data_movimentacao).strftime("%d/%m/%Y") if matricula.data_movimentacao != None else "-" }"
                   
                    aria-describedby="emailHelp" 
                    placeholder="Ano" 
                    value="{matricula.ano}"
                    disabled
                  /> 
                   <input        
                    type="text"     
                    class="form-control m-2" 
                   
                    aria-describedby="emailHelp" 
                    placeholder="Ano" 
                    value=" {descritivo_situacao}"
                    disabled
                  /> 
                      
                      <input        
                    type="text"     
                    class="form-control m-2" 
                    
                    aria-describedby="emailHelp" 
                    placeholder="Ano" 
                    value="{matricula.classe}"
                    disabled
                  /> 
                </div>"""
    
    return HttpResponse(dados_matricula)


