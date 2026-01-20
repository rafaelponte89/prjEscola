from datetime import date
from rh.models.pessoa import Pessoas


def retornarNomeMes(chave):
    meses = {
        1: "janeiro",
        2: "fevereiro",
        3: "março",
        4: "abril",
        5: "maio",
        6: "junho",
        7: "julho",
        8: "agosto",
        9: "setembro",
        10: "outubro",
        11: "novembro",
        12: "dezembro"
    }

    return meses.get(chave, "")

# determina se o ano é bissexto
def bissexto(ano):

    if ano % 400 == 0:
        return True
    else:
        if ano % 4 == 0:
            if ano % 100 == 0:
                return False
            return True
        
def retornar_meses(ano=0):
    meses = {
        'janeiro':[1,31],
        'fevereiro':[2,29 if bissexto(ano) else 28],
        'março':[3,31],
        'abril':[4,30],
        'maio':[5,31],
        'junho':[6,30],
        'julho':[7,31],
        'agosto':[8,31],
        'setembro':[9,30],
        'outubro':[10,31],
        'novembro':[11,30],
        'dezembro':[12,31]
    }

    return meses

def criar_estrutura_meses():
    estrutura_meses_nome = {}
    dias = []
    # construção dos meses
    meses = retornar_meses()
    for k in meses.keys():
        for j in range(31):
            dias.append('-')
        estrutura_meses_nome[k] = dias
        
        dias = []

    return estrutura_meses_nome

# refatorada 17/07/2025
def configurar_meses_v4(ano, pessoa_id):
    '''A versão atual do método leva em consideração data de admissão e saída para fazer a devida configuração'''
    pessoa = Pessoas.objects.get(pk=pessoa_id)
    
    data_inicial = pessoa.admissao
    data_final = pessoa.saida or date.max
    
    meses = criar_estrutura_meses()
    mes_info = retornar_meses(ano)
    

    for nome_mes, (numero, qtd_dias) in mes_info.items():
        for dia in range(qtd_dias):
            try:
                data_atual = date(ano,numero,dia + 1)
            except ValueError:
                continue

            if  data_inicial <= data_atual < data_final:
                meses[nome_mes][dia] = 'C'

   
    return meses