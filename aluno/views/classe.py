from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string

from aluno.models.ano import Ano
from aluno.models.matricula import Matricula
from utilitarios.utilitarios import criarMensagem

from aluno.models.classe import Classe
from aluno.services.mensagem import criarMensagemJson

from aluno.forms.classe import FrmClasseUpdate
from aluno.utils.texto import padronizar_nome


# Create your views here.
def classe(request): 
    context = {
        'periodos': Classe.PERIODO_CHOICES,
        
    }   
    return render(request, 'aluno/classe/classe.html', context)


def buscar(request):
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
        ano = request.GET.get('ano')
        ano = Ano.objects.get(pk=ano)
        serie = request.GET.get('serie')
        turma = request.GET.get('turma')
        periodo = request.GET.get('periodo')
    
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
        classe = request.GET.get("classe")
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

# versão 3 em abas 12/01/2025
def carregarAnoAtual(ano):
    ano = Ano.objects.get(pk=ano)
    classe = Classe.objects.filter(ano=ano).order_by('periodo').order_by('turma').order_by('serie')
    abas = ''
    series = []
    conteudos = ''
    tabela = ''

    for c in classe:
       
        if c.serie not in series:
            series.append(c.serie)
            tabela = buscarTabelaTurmas(ano, c.serie)
           
            abas += f"""
                <li class="nav-item">
                 <a class="nav-link" id="aba-{c.serie}" data-toggle="tab" href="#cont-aba-{c.serie}" role="tab" aria-controls="{c.serie}">{c.serie}º Ano</a>
                </li>
            """
            
            conteudos += f"""
                     <div class="tab-pane fade" id="cont-aba-{c.serie}" role="tabpanel" aria-labelledby="{c.serie}">
                     
                     {tabela}
                     
                     </div>"""
            tabela = ''
    abas = f"""<ul class="nav nav-tabs mt-4" id="myTab" role="tablist">{abas}</ul>
               <div class="tab-content" id="myTabContent">
                {conteudos}
                </div>
            """

        
    return abas




def buscarTabelaTurmas(ano, serie):
    classe = Classe.objects.filter(ano=ano).filter(serie=serie).order_by('periodo').order_by('turma').order_by('serie')
    tabela=""
    tabela_estrutura=""

    for c in classe:
        periodo = Classe.retornarDescricaoPeriodo(c)

        tabela += f"""
        
        
        <tr><td class='text-center '>{c.serie}</td><td class='text-center'>{c.turma}</td><td class='text-center'>{periodo}</td> <td class='text-center'>  <button type="button" class="btn btn-outline-dark btn-lg atualizar"
                    value={c.id} data-bs-toggle="modal" data-bs-target="#atualizarModal"> 
                            <i class="bi bi-arrow-repeat"></i> 
                        </button> </td>
                       
                        <td class='text-center'>  <button type="button" class="btn btn-outline-dark btn-lg visualizar"
                        value={c.id} data-bs-toggle="modal" data-bs-target="#visualizarClasseModal"> 
                            <i class="bi bi-eye"></i>
                        </button> </td>
                        </tr>
                        """
    tabela_estrutura = f"""<table
      id="tabela"
      class="table table-hover table-responsive table-bordered table-success m-2"
    >
      <thead class="text-center">
       
        <th>Série</th>
        <th>Turma</th>
        <th>Período</th>
        <th>Atualizar</th>
      
        <th>Visualizar</th>
      </thead>
      <tbody id="corpoTabelaTurmas">
        {tabela}
      </tbody>
    </table>"""
    
    
    return tabela_estrutura
 
#Listar classes em HTML   
def listar(request):
    ano = int(request.GET.get("ano"))
    return HttpResponse(carregarAnoAtual(ano))


#Visualizar alunos da classe
def exibirClasses(request):
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
    ano = request.GET.get('ano')
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