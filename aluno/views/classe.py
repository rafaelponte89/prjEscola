from django.db.models import Q
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from collections import defaultdict


from aluno.models.ano import Ano
from aluno.models.matricula import Matricula
from aluno.utils.mensagem_http import criarMensagem

from aluno.models.classe import Classe

from aluno.forms.classe import FrmClasseUpdate
from aluno.utils.texto import padronizar_nome
from aluno.services.classe import renderizarTabela

# Create your views here.
def classe(request): 
    context = {
        'periodos': Classe.PERIODO_CHOICES,
        
    }   
    return render(request, 'aluno/classe/classe.html', context)

def buscar_classe(request):
    classe = request.GET.get('classe')
    classe = Classe.objects.get(pk=classe)
    form = FrmClasseUpdate(instance=classe)
   
    return render(
        request,
        "aluno/classe/partials/form_update.html",
        {"form": form, "classe": classe}
    )
    
#Gravar classe
def gravar(request):
    try:
        ano = request.POST.get('ano')
        ano = Ano.objects.get(pk=ano)
        serie = request.POST.get('serie')
        turma = request.POST.get('turma')
        periodo = request.POST.get('periodo')
    
        classe = Classe()
        classe.ano = ano
        classe.serie = serie
        classe.turma = turma.upper()
        classe.periodo = periodo
        classe.save()
    
        return criarMensagem('Classe salva com sucesso!!!', 'success')

    except:
        return criarMensagem('Erro ao gravar!!!', 'danger')
    
#Deletar classe
def deletar(request):
    try:
        classe = request.POST.get("classe")
        classe = Classe.objects.get(pk=classe)
        classe.delete()
        return criarMensagem('Classe deletada com sucesso!!!','warning')
    except Exception as erro:
        return criarMensagem(erro, 'danger')


#Atualizar classe
def atualizar(request):

    try:
        classeid = request.POST.get('classe')
        classe = Classe.objects.get(pk=classeid)
        serie = request.POST.get('serie')
        turma = padronizar_nome(request.POST.get('turma'))
        periodo = request.POST.get('periodo')
        ano = request.POST.get('ano')
        ano = Ano.objects.get(pk=ano)
        
        classe.serie = serie
        classe.turma = turma
        classe.periodo = periodo
        classe.ano = ano
        classe.save()
        return criarMensagem("Classe Atualizada com Sucesso!!!","success")
    except Exception as e:
        print(e)
        return criarMensagem("Erro ao Atualizar Classe!!!", "danger")
 
#Listar classes em HTML   
def listar_classe(request):
    ano = request.GET.get("ano")
    ano = Ano.objects.get(pk=ano)

    classes = Classe.objects.filter(
        ano=ano
    ).order_by("serie", "turma", "periodo")

    classes_por_serie = defaultdict(list)
    for c in classes:
        classes_por_serie[c.serie].append(c)

    html = renderizarTabela(classes_por_serie, request)

    return JsonResponse({
        'success': True,
        'html': html
    })

def exibirClasse(request):
    codigo_classe = request.GET.get('classe')
    classe = Classe.objects.get(pk=codigo_classe)
    matriculas = Matricula.objects.filter(Q(classe=classe)).order_by('numero').values('numero', 'aluno__nome')
   
    periodo = Classe.retornarDescricaoPeriodo(classe)
        
    html = render_to_string("aluno/classe/partials/modal_exibir_classe.html",
                             {"serie": classe.serie,
                              "turma": classe.turma,
                              "periodo": periodo,
                              "matriculas": matriculas},)
    return JsonResponse({
        "html": html,
    })

def contar(serie,ano,periodo):
    classes = Classe.objects.filter(ano=ano).filter(serie=serie).filter(periodo=periodo)
    
    return len(classes)

# Gera a turma
def gerarTurma(serie, ano, series, periodo, turma):
    for i in range(serie):
        classe = Classe()
        classe.ano = ano
        classe.serie = series
        classe.turma = chr(turma)
        classe.periodo = periodo
        classe.save()
        turma += 1
    return turma

# Gera as turmas
def gerarTurmas(request):
    ano = request.POST.get('ano')
    ano = Ano.objects.get(pk=ano)
    turma = 65
    
    for s in range(1, 10):
        serie_manha = int(request.POST.get('m'+str(s)))
        serie_tarde = int(request.POST.get('t'+str(s)))
        serie_integral = int(request.POST.get('i'+str(s)))

        if (serie_manha) > 0:
            turma = gerarTurma(serie_manha, ano, s,"M",turma )

        if (serie_tarde) > 0: 
            turma = gerarTurma(serie_tarde, ano, s,"T",turma )

        if (serie_integral) > 0:
            turma = gerarTurma(serie_integral, ano, s,"I",turma )

        turma = 65
                
    return HttpResponse("Geradas as salas") 


def exibirQuadro(request):
    ano_id = request.GET.get("ano")
    ano = Ano.objects.get(pk=ano_id)

    classes = Classe.objects.filter(ano=ano)
    desabilita = classes.exists()

    linhas = []

    for i in range(1, 10):
        linhas.append({
            "serie": i,
            "manha": contar(i, ano, "M"),
            "tarde": contar(i, ano, "T"),
            "integral": contar(i, ano, "I"),
        })

    return render(
        request,
        "aluno/classe/partials/quadro.html",
        {
            "ano": ano,
            "linhas": linhas,
            "desabilita": desabilita,
        }
    )
    
def carregar_classes(request):
    ano = request.GET.get('ano')
    ano = Ano.objects.get(pk=ano)
    classes = Classe.objects.filter(ano=ano)
    opcoes = "<option value='0'>Selecione</option>"
                                            
    for c in classes:
        periodo = Classe.retornarDescricaoPeriodo(c)
        opcoes += f"<option value={c.id}>{c.serie}º {c.turma} - {periodo}</option>"
        
    return HttpResponse(opcoes) 