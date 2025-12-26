from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse


from aluno.models.ano import Ano
from aluno.models.matricula import Matricula
from utilitarios.utilitarios import criarMensagem

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
    print(request.POST)
    print(request.GET)

    ano = request.GET.get("ano")
    ano = Ano.objects.get(pk=ano)
    classes = Classe.objects.filter(ano=ano).order_by("periodo","serie","turma")
   
    html = renderizarTabela(classes, request)
    print(html)
    return JsonResponse({
        'success': True,
        'html': html
    })

def exibirClasse(request):
    codigo_classe = request.GET.get('classe')
    classe = Classe.objects.get(pk=codigo_classe)
    matriculas = Matricula.objects.filter(Q(classe=classe)).order_by('numero')
    linhas = ''
    periodo = Classe.retornarDescricaoPeriodo(classe)
        
    for m in matriculas:
        linhas += f"""<tr><td>{m.numero}</td>  <td>{m.aluno.nome}</td></tr>"""

    tabela = f"""<div class="row mt-3">
      <div class="col-12">
    <h5 class='bg-body-secondary d-flex rounded-5 justify-content-center p-2'><strong>{classe.serie}º{classe.turma} - {periodo} </strong></h5>

    <table id="tabelaAlunos" class="table table-hover table-responsive">
      <thead>
        <th>Nº</th> 
        <th>Nome do Aluno</th>
      </thead>
      <tbody>
        {linhas}
      </tbody>
    </table>
    </div>
    </div>"""
  
    return HttpResponse(tabela)  

   

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
        serie_manha = int(request.GET.get('m'+str(s)))
        serie_tarde = int(request.GET.get('t'+str(s)))
        serie_integral = int(request.GET.get('i'+str(s)))

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