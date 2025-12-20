from rh.app_ficha_cem.models import Pontuacoes

def deletar_pontuacao_ano(pessoa, ano):
    if not ano:
        return
    Pontuacoes.objects.filter(pessoa=pessoa).filter(ano__in=ano).delete()


def criar_salvar_pontuacao(ano, funcao, cargo, ue, pessoa):
    pontuacao = Pontuacoes(ano=ano,funcao=funcao,cargo=cargo,ue=ue,pessoa=pessoa)
    pontuacao.save()