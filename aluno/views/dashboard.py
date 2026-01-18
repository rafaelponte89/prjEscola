from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render
from aluno.models.ano import Ano
from aluno.models.matricula import Matricula

# Create your views here.

def dashboard(request):
    return render(request, 'aluno/dashboard/dashboard.html',)

def contar_por_periodo_aggregate(ano, situacoes_validas=['C', 'P']):
    contagens = Matricula.objects.filter(ano=ano, situacao__in=situacoes_validas).aggregate(
        manha=Count('id', filter=Q(classe__periodo='M')),
        tarde=Count('id', filter=Q(classe__periodo='T')),
        integral=Count('id', filter=Q(classe__periodo='I')),
    )
  
    return contagens['manha'], contagens['tarde'], contagens['integral']

def visualizar_alunos_periodo(request):

    ano = Ano.objects.get(pk=request.GET.get('ano'))
    manha, tarde, integral = contar_por_periodo_aggregate(ano)
    dados = {
        'Manhã': manha,
        'Tarde': tarde,
        'Integral': integral
    }

    return JsonResponse(dados, safe=False)

def visualizar_alunos_mes(request):

    ano = request.GET.get('ano')
    dados = {
        'Janeiro': 0,
        'Fevereiro': 0,
        'Março': 0,
        'Abril': 0,
        'Maio': 0,
        'Junho': 0,
        'Julho': 0,
        'Agosto': 0,
        'Setembro': 0,
        'Outubro': 0,
        'Novembro': 0,
        'Dezembro': 0
    }
    mes = 0
    for k in dados.keys():
        mes += 1
        dados[k] =  (Matricula.objects.exclude(situacao='REMA').filter(ano=ano).filter(data_matricula__month__lte=mes).count()
        -Matricula.objects.filter(situacao='BXTR').filter(ano=ano).filter(data_movimentacao__month__lte=mes).count()
        -Matricula.objects.filter(situacao='NFCP').filter(ano=ano).filter(data_movimentacao__month__lte=mes).count()
        -Matricula.objects.filter(situacao='P').filter(ano=ano).filter(data_movimentacao__month__lte=mes).count())
    
    return JsonResponse(dados, safe=False)
    





