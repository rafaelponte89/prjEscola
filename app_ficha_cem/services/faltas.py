from datetime import datetime, timedelta
from app_ficha_cem.models import Faltas_Pessoas

# faz a pesquisa e incremento para verificar se existe falta lançada naquela data, impedindo lançamento em data
# que já exista falta computada
def lancar_falta(data_lanc, qtd_dias, pessoa_id):
    # Normaliza a data de lançamento para meia-noite (sem hora)
    data_lanc = datetime(data_lanc.year, data_lanc.month, data_lanc.day)

    # Cria o conjunto de datas a serem lançadas
    datas_lanc = {data_lanc + timedelta(days=i) for i in range(qtd_dias)}

    # Consulta apenas as faltas da pessoa no mesmo ano da data de lançamento
    faltas = Faltas_Pessoas.objects.filter(
        pessoa_id=pessoa_id,
        data__year=data_lanc.year
    )

    # Cria um conjunto com todas as datas já lançadas
    datas_existentes = set()
    for falta in faltas:
        inicio = datetime(falta.data.year, falta.data.month, falta.data.day)
        for i in range(falta.qtd_dias):
            datas_existentes.add(inicio + timedelta(days=i))

    # Verifica se há interseção entre as datas
    conflito = datas_lanc.isdisjoint(datas_existentes)

    return conflito
