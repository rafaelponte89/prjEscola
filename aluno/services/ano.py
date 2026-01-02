from aluno.models.ano import Ano
from aluno.models.matricula import Matricula
from aluno.models.aluno import Aluno    

def efetuar_lancamentos_fechamento_ano(ano):
    matriculas = Matricula.objects.filter(ano=ano)
    lista_alunos = []
    lista_matriculas = []
    for matricula in matriculas:
        aluno = Aluno.objects.get(pk=matricula.aluno.rm)
        if ano.fechado and matricula.situacao == 'C':
            matricula.situacao = 'P'
            aluno.status = Aluno.STATUS_ARQUIVADO
        else:
            if matricula.situacao == 'P':
                matricula.situacao = 'C'
                aluno.status = Aluno.STATUS_ATIVO
            else:
                if matricula.situacao == 'R':
                    matriculas_cursando = Matricula.objects.filter(aluno=aluno).filter(situacao='C')
                    matriculas_cursando.delete()
                    matricula.situacao = 'C'
                    aluno.status = Aluno.STATUS_ATIVO
        lista_alunos.append(aluno)
        lista_matriculas.append(matricula)

    Aluno.objects.bulk_update(lista_alunos, ['status'])
    Matricula.objects.bulk_update(lista_matriculas, ['situacao'])
   