from django.db.models import Q
from aluno.models.matricula import Matricula
from aluno.models.aluno import Aluno
from aluno.models.classe import Classe
from aluno.utils.mensagem_http import criarMensagemModal
from django.db import transaction
from django.db import transaction

# Verificar se existe matrícula ativa no ano, se não possuir pode matricular
# Se possuir não pode
def verificar_matricula_ativa_no_ano(ano, rm, situacao='C'):
    matriculas = Matricula.objects.filter(Q(ano=ano) & Q(aluno_id=rm) & Q(situacao=situacao))  
    return False if matriculas else True 

def deletar_todas_matriculas_da_classe(classe):
    matriculas = Matricula.objects.select_related("aluno").filter(classe=classe)

    alunos_ids = matriculas.values_list("aluno_id", flat=True)

    with transaction.atomic():
        Aluno.objects.filter(rm__in=alunos_ids).update(status=Aluno.STATUS_ARQUIVADO)
        matriculas.delete()
        
def matricular_aluno(ano, classe, aluno, numero, data_matricula, data_movimentacao=None, situacao='C', m_sucesso='Matriculado com Sucesso!!!', m_tipo='M'):
   
    if ano.fechado:
        return criarMensagemModal(f'Ano {ano} fechado!','danger')
    else:
        if (verificar_matricula_ativa_no_ano(ano=ano, rm=aluno)):
            matricula = Matricula.objects.filter(aluno=aluno)

            # Se aluno matriculado na mesma serie o status de promovido é alterado para reprovado e salvo
            for m in matricula:
                if m.classe.serie == classe.serie:
                    if m.situacao == 'P':
                        m.situacao = 'R'
                        m.save()

            matricula_nova = Matricula(ano=ano, classe=classe, aluno=aluno, 
                                    numero=numero,
                                    data_matricula=data_matricula, 
                                    data_movimentacao=data_movimentacao,
                                    situacao=situacao,
                                    )

            matricula_nova.save()
            aluno.status = Aluno.STATUS_ATIVO
            aluno.save()
            if m_tipo != 'M':
                return criarMensagemModal(m_sucesso,'success')
            else:
                return criarMensagemModal(m_sucesso,'success')
        else:
            return criarMensagemModal('Aluno com Matricula Ativa!','danger')

def movimentar_remanejamento(**kwargs):
    classe_remanejamento = kwargs["classe_remanejamento"]
    matricula = kwargs["matricula"]
    ano = kwargs["ano"]
    data_movimentacao = kwargs["data_movimentacao"]
    matricula.save()          
    classe = Classe.objects.get(pk=classe_remanejamento)
    resposta = matricular_aluno(ano,classe, matricula.aluno,
                                    Classe.retornarProximoNumeroClasse(Matricula, classe),
                                    data_movimentacao, m_sucesso="Remanejamento Efetuado!")
    return resposta

def movimentar_transferencia(**kwargs):
    matricula = kwargs["matricula"]
    aluno = Aluno.objects.get(pk=matricula.aluno.rm)
    aluno.status = Aluno.STATUS_ARQUIVADO
    aluno.save()
    matricula.save()
    return criarMensagemModal("Transferência efetuada!", "success")

def listar_por_classe(classe, ordem="numero"):
    matriculas = Matricula.objects.filter(classe=classe).order_by(ordem)
    return matriculas

@transaction.atomic
def reordenar_matriculas_alfabetica(classe):
    matriculas = (
        Matricula.objects
        .filter(classe=classe)
        .select_related('aluno')
        .order_by('aluno__nome')
    )

    for index, matricula in enumerate(matriculas, start=1):
        matricula.numero = index
        matricula.save(update_fields=['numero'])

    return matriculas
