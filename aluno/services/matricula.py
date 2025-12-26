from django.db.models import Q
from aluno.models.matricula import Matricula
from aluno.models.aluno import Aluno

# Verificar se existe matrícula ativa no ano, se não possuir pode matricular
# Se possuir não pode
def verificar_matricula_ativa_no_ano(ano, rm, situacao='C'):
    matriculas = Matricula.objects.filter(Q(ano=ano) & Q(aluno_id=rm) & Q(situacao=situacao))  
    return False if matriculas else True 

# Verificar se existe matrícula ativa, se não possuir pode matricular
def verificar_matricula_ativa(rm, situacao='C'):
    matriculas = Matricula.objects.filter(Q(aluno_id=rm) & Q(situacao=situacao) )  
    return False if matriculas else True 
  
# Veriricar se aluno já foi matriculado na mesma série  no mesmo ano 09/10/2024       
def verificar_matricula_na_mesma_serie_ano_corrente(matricula,serie):

    for m in matricula:
        print(m.classe.serie)
    return False if matricula else True

# Veriricar se aluno já foi matriculado na mesma série qualquer ano 09/10/2024       
#def verificar_matricula_na_mesma_serie_mesmo_ano(rm, serie):
#    matriculas = Matricula.objects.filter(Q(aluno_id=rm) & Q(serie=serie))
#    return False if matriculas else True


def deletar_todas_matriculas_da_classe(classe):
    matriculas = Matricula.objects.filter(classe=classe)
    matriculas.delete()
    for matricula in matriculas:
        aluno = Aluno.objects.filter(rm=matricula.aluno.rm)
        aluno.status = 0
        aluno.save()