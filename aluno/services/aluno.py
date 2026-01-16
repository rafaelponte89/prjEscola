from aluno.models.matricula import Matricula
from aluno.models.telefone import Telefone
from aluno.models.aluno import Aluno
from django.db.models import Q
from django.template.loader import render_to_string


def renderizarTabela(alunos, nomes_duplicados, request):
    
    html = render_to_string(
            'aluno/aluno/partials/tabela.html',
            {
                'alunos': alunos,
                'nomes_duplicados': nomes_duplicados,
                'retornar_ultima_matricula_ativa': retornar_ultima_matricula_ativa,
                'retornar_numeros_telefones': retornar_numeros_telefones,
            },
            request=request
        )
    return html

def buscar_duplicados(alunos):
   
    nomes_rm = {}
    duplicados = {}
    for aluno in alunos:
        nome = aluno.nome.strip().upper()
        if aluno.status != 1:
            nomes_rm.setdefault(nome, []).append(aluno.rm)
   
    duplicados = {k: v for k, v in nomes_rm.items() if len(v) > 1}
            
    return duplicados.keys()

def retornar_ultima_matricula_ativa(aluno):
    ultima_matricula = Matricula.objects.filter(aluno=aluno).filter(situacao='C').order_by('-ano').first()
    return ultima_matricula.classe if ultima_matricula else '-'
 
def retornar_numeros_telefones(aluno):
    telefones = (Telefone.objects.filter(aluno=aluno)
                 .values_list("numero", flat=True))
    texto_numeros = ("" .join(f"<span class='m-1'>{numero}</span>" 
                              for numero in telefones))
    return texto_numeros
  
def retornar_telefones(aluno):
    telefones = Telefone.retornarListaTelefones()
    telefones_aluno = Telefone.objects.filter(aluno=aluno)
    print(telefones)
    for telefone in telefones_aluno:
        print(telefone.contato)
        
def gerarIntervalo(rm_inicial, rm_final):
    
    alunos = Aluno.objects.filter(Q(rm__gte=rm_inicial) & Q(rm__lte=rm_final)).values('nome', 'rm', 'status').order_by('rm')
    return alunos

def pesquisar_alunos_por_nome(nome, filtro):
    # Filtragem normal
    qs = Aluno.objects.filter(nome__icontains=nome)
    if filtro == 'a':
        qs = qs.filter(status=Aluno.STATUS_ATIVO)
    alunos = qs[:10]
    return alunos

def calcular_idade(data_nascimento, data_referencia):
    # Calcule a diferença de anos
    idade = data_referencia.year - data_nascimento.year

    # Ajuste se o aniversário ainda não tiver ocorrido naquele ano
    if (data_referencia.month, data_referencia.day) < (data_nascimento.month, data_nascimento.day):
        idade -= 1

    return idade

