from datetime import datetime
import os
import tempfile

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string

from aluno.models.aluno import Aluno
from aluno.models.ano import Ano
from aluno.models.classe import Classe
from aluno.forms.matricula import ImportarMatriculasForm
from utilitarios.utilitarios import (criarMensagem, criarMensagemModal)
from aluno.services.mensagem import criarMensagemJson

from aluno.models.matricula import Matricula

from aluno.services.predicao import prever_idade_serie
from aluno.services.matricula import matricular_aluno, movimentar_transferencia, movimentar_remanejamento
from aluno.services.matricula import reordenar_matriculas_alfabetica, listar_por_classe
from aluno.services.matricula_importar import importar_matriculas_pdf
# Create your views here.

def matricula(request):
    return render(request, 'aluno/matricula/matricula.html')

def adicionar(reqeust):
    pass

def deletar(request):
    pass

#Buscar aluno
def buscarAluno(request):
    nome = request.GET.get('nome', '')

    alunos = (
        Aluno.objects
        .filter(nome__icontains=nome)
        .order_by('nome')[:5]
    )
    return render(request, 'aluno/matricula/partials/tabela_alunos.html', {
        'alunos': alunos
    })
  
def matricular_aluno_ia(request):
    aluno = Aluno.objects.get(pk=request.POST.get('aluno'))
    ano = Ano.objects.get(pk=request.POST.get('ano'))
    previsao = prever_idade_serie(aluno)[0]
    classes = Classe.objects.filter(ano=ano).filter(serie=previsao)
    menor = 99
    classe_sel=''
    
    for classe in classes:
        matriculas = Matricula.objects.filter(classe=classe)
        if(len(matriculas)) <= menor:
            menor = len(matriculas)
            classe_sel= classe
  
    try:
        resposta =  matricular_aluno(ano=ano, aluno=aluno,classe=classe_sel, numero=Classe.retornarProximoNumeroClasse(Matricula, classe_sel),
                     data_matricula=datetime.now(), m_sucesso=f'Matriculado com sucesso! Na Classe {classe} - Ano: {ano}')
            
        return resposta
    except Exception as err:
        return criarMensagem(f'Não existe {previsao}º ano para matricular o aluno!','danger')
    
#Exibir tela da matrícula  
def exibirTelaMatricula(request):
    codigo_classe = request.GET.get("classe")
    classe = Classe.objects.get(pk=codigo_classe)
    periodo = Classe.retornarDescricaoPeriodo(classe)
   
    return JsonResponse({"serie":classe.serie, 
                         "turma": classe.turma , 
                         "periodo": periodo,
                         "cod_classe": classe.id})

#Adicionar aluno na classe        
def adicionarNaClasse(request):
    try:
        aluno = Aluno.objects.get(pk=request.GET.get('aluno'))
        ano = request.GET.get('ano')
        ano = Ano.objects.get(pk=ano)
        classe = Classe.objects.get(pk=request.GET.get('classe'))
        resposta = matricular_aluno(ano, classe, aluno, 
                              Classe.retornarProximoNumeroClasse(Matricula, classe),
                              request.GET.get('data_matricula'))
        return resposta
    
    except Exception:    
        return criarMensagemModal(f"Erro ao efetuar a Matrícula", "danger")

def movimentar(request):
    
    try:
        matricula = Matricula.objects.get(pk=request.GET.get('matricula'))
        data_movimentacao = datetime.strptime(request.GET.get('data_movimentacao'),'%Y-%m-%d').date()
        
        STATUS_MOVIMENTACAO = {
            "REMA": movimentar_remanejamento,
            "BXTR": movimentar_transferencia,
        }
           
        if (data_movimentacao > matricula.data_matricula):
            movimentacao = request.GET.get('movimentacao')
            matricula.situacao = movimentacao
            ano = Ano.objects.get(pk=request.GET.get('ano'))
            matricula.ano = ano
            matricula.data_movimentacao = data_movimentacao
            
            return STATUS_MOVIMENTACAO[movimentacao](matricula=matricula, ano=ano, data_movimentacao=data_movimentacao, 
                                                     classe_remanejamento=request.GET.get('classe_remanejamento'))
        else:
            return criarMensagem("Data da movimentação deve ser maior que a data da matrícula!", "warning")

    except Exception as erro:
        print(erro)
        return criarMensagem(f"Erro ao efetuar o Remanejamento!{erro}",
                             "danger")


def ordenar_em_alfabetica(request):
    classe_id = request.GET.get('classe')

    matriculas = reordenar_matriculas_alfabetica(classe_id)

    return render(request, 'aluno/matricula/partials/tabela_matriculas.html', {
        'matriculas': matriculas,
    })


def carregar_movimentacao(request):
   
    movimentacoes = Matricula.retornarSituacao()
    opcoes = "<option value='0'>Selecione</option>"
                                            
    for m in movimentacoes:
     
        if m[0] == "BXTR":
            situacao = "TRANSFERIDO"
        elif m[0] == "REMA":
            situacao = "REMANEJADO"
        elif m[0] == "NCFP":
            situacao = "Ñ COMP. FORA PRAZO"
            
        if m[0] not in ['C','P','R']:
            opcoes += f"<option value={m[0]}>{situacao} </option>"
        
    return HttpResponse(opcoes)

def carregar_classes_remanejamento(request):
    ano = request.GET.get('ano')
    ano = Ano.objects.get(pk=ano)
     
    classe_atual = Classe.objects.get(pk=request.GET.get('serie'))
    classes = Classe.objects.filter(ano=ano, serie=classe_atual.serie)
    classes = classes.exclude(pk=request.GET.get('serie'))
    opcoes = "<option value='0'>Selecione</option>"
                                            
    for c in classes:
       periodo = Classe.retornarDescricaoPeriodo(c)
       opcoes += f"<option value={c.id}>{c.serie}º {c.turma} - {periodo}</option>"
        
    return HttpResponse(opcoes) 

def excluir_matricula(request):
  
        matricula = request.GET.get('matricula')
        matricula = Matricula.objects.get(pk=matricula)
        aluno = Aluno.objects.get(pk=matricula.aluno.rm)
        if matricula:
            matricula.delete()
            aluno.status = 0
            aluno.save()
            return criarMensagem("Matrícula excluída com sucesso!", "success")
    
def buscar_matricula(request):
    matricula = request.GET.get('matricula')
    matricula = Matricula.objects.get(pk=matricula)
   
    matricula = {"id_matricula": matricula.id, "rm_aluno": matricula.aluno.rm, "nome_aluno": matricula.aluno.nome, 
                 "data_movimentacao": matricula.data_movimentacao if matricula.data_movimentacao else datetime.now().date() }
  
    return JsonResponse (matricula)

def carregar_matriculas(request):
    classe = request.GET.get('classe')
    matriculas = listar_por_classe(classe)

    if matriculas:
        return render(request, 'aluno/matricula/partials/tabela_matriculas.html', {
            'matriculas': matriculas,
        })
    else:
        return criarMensagem("Sem alunos matriculados", "info")

        
def upload_matriculas(request):
    if request.method == "POST":
        form = ImportarMatriculasForm(request.POST, request.FILES)
        classe = request.POST.get('classe')
    
        ano = request.POST.get('ano')
        data_matricula = request.POST.get('data_matricula')

        if form.is_valid():
            arquivo = form.cleaned_data["arquivo"]

            if arquivo.content_type != "application/pdf":
                return JsonResponse(
                                    {"mensagem": criarMensagemJson("Somente arquivos PDF são permitidos", "danger")},
                    status=400
                )

            sufixo = os.path.splitext(arquivo.name)[1]

            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=sufixo) as tmp:
                    for chunk in arquivo.chunks():
                        tmp.write(chunk)
                    caminho_pdf = tmp.name
                resultado = importar_matriculas_pdf(caminho_pdf, classe, ano, data_matricula)
            finally:
                if os.path.exists(caminho_pdf):
                    os.remove(caminho_pdf)
                    
            
            html = render_to_string(
                "aluno/matricula/partials/tabela_matriculas.html",
                {"matriculas": listar_por_classe(classe)},
                request=request
            )

            return JsonResponse({
                "html": html,
                "mensagem": criarMensagemJson(f"Importação concluída com sucesso!!", 
                                              "success")
            })

    

    
    
