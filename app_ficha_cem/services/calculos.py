from datetime import datetime, timedelta
from app_ficha_cem.models import Faltas_Pessoas, Pontuacoes

from .configuracoes import configurar_meses_v4

def contar_dias(data_inicial, data_final):
    dias = (data_final - data_inicial ).days + 1

    return dias

# desconta faltas conforme a data inicial e data final levando em conta 
# a tolerancia 
def faltas_a_descontar(ano,pessoa, tolerancia=6):
    # atribuição 
    data_inicial = datetime(ano-1,11,1)
    data_final = datetime(ano,10,31)
    maior = Faltas_Pessoas.objects.all().filter(data__gte=f'{ano-1}-11-01')
    maior = maior.filter(pessoa=pessoa)
    menor = Faltas_Pessoas.objects.all().filter(data__lte=f'{ano}-10-31')
    menor = menor.filter(pessoa=pessoa)
    atrib = maior.intersection(menor)
    datas = []
   
    for fp in atrib:
        if fp.falta.tipo in ['J','AM','AO']:
            data = datetime(fp.data.year, fp.data.month, fp.data.day)
            
            for dias in range(1,fp.qtd_dias):
                if data >= data_inicial and data <= data_final:
                    datas.append(data)
                data += timedelta(days=1)
                data = datetime(data.year, data.month, data.day)
            else:
                if data >= data_inicial and data <= data_final:
                    datas.append(data)
               
    n_faltas = len(datas)
  
    if n_faltas >= tolerancia:
        n_faltas -= tolerancia
    else:
        n_faltas = 0

    return n_faltas


# conta os tipos de faltas construindo um dicionário
def contar_tipos_faltas(faltas):

    # insere no dicionario nova falta e atualiza quantidade da falta
    qtd = 0
    tipo_faltas ={}
    for f in faltas:
        sigla = f.falta.tipo
        descricao = f.falta.descricao
      
        if sigla not in tipo_faltas.keys():
           qtd = f.qtd_dias
           tipo_faltas[sigla] = [descricao, qtd]
        else:
            qtd = tipo_faltas[sigla][1]
            qtd += f.qtd_dias
            tipo_faltas[sigla][1] = qtd
    
    return tipo_faltas


# dado um determinado ano acumula dias por meses
def acumular_dias(ano,pessoa_id,acumulado=0):
    meses = configurar_meses_v4(ano,pessoa_id)
    
    dias_acumulados_por_mes = {}
    
    dias = 0
    for k,v in meses.items():
        for d in v:
            if d != '-':
                dias += 1
        acumulado += dias
        if k == 'outubro':
            acumulado -=  faltas_a_descontar(ano,pessoa_id)
            dias_acumulados_por_mes[k] = acumulado 
        else:
            dias_acumulados_por_mes[k] = acumulado
        dias = 0
    
   
    return dias_acumulados_por_mes


def calcular_data_pedido(data_falta):
    """
    Calcula a data do pedido como 5 dias úteis antes da data da falta.
    Um dia útil é considerado de Segunda a Sexta-feira (weekday < 5).
    :param data_falta_str: String com a data da falta no formato "dd/mm/aaaa".
    :return: Objeto datetime para a data do pedido.
    """
    

    dias_uteis_a_subtrair = 5
    data_calculada = data_falta

    # 2. Iterar subtraindo 1 dia por vez e checando se é dia útil
    while dias_uteis_a_subtrair > 0:
        data_calculada -= timedelta(days=1)
        
        # O weekday() retorna 0 para Segunda-feira e 6 para Domingo.
        # Dias úteis (Segunda a Sexta) são 0, 1, 2, 3, 4.
        if data_calculada.weekday() < 5: 
            dias_uteis_a_subtrair -= 1

    # 3. Retorna a data calculada (5 dias úteis antes)
    return data_calculada

# função recursiva que determina se a data é útil (excluindo sábado e domingo) para o tipo P, senão retorna própria data
def data_util(data, tp='P'):
    
    if tp == 'P':
        if (data.weekday() != 6 and data.weekday() != 5):
            return data
        data = data + timedelta(days=1)
        return data_util(data)
    return data


def gerar_pontuacao_atribuicao(ano,pessoa, tipo='c'):
    '''a - ano anterior, c - ano corrente '''

    data_bas_ini = datetime.strptime(f'{ano-1}-11-01','%Y-%m-%d',).date()
    data_bas_fim = datetime.strptime(f'{ano}-10-31','%Y-%m-%d').date()

    if pessoa.admissao > data_bas_ini:
        data_bas_ini = pessoa.admissao

    dias = contar_dias(data_bas_ini, data_bas_fim)

    q1 = Pontuacoes.objects.filter(ano=ano-1) # ano anterior
    q2 = Pontuacoes.objects.filter(pessoa=pessoa)

    pontuacao_anterior = q1.intersection(q2)
    
    # ano anterior
    if tipo == 'a':
        if len(pontuacao_anterior) == 0:
            cargo = 0
            funcao = 0
            ue = 0
           
        else:
            cargo = pontuacao_anterior[0].cargo_atrib
            funcao = pontuacao_anterior[0].funcao_atrib
            ue = pontuacao_anterior[0].ue_atrib
 
    else:
        # ano corrente
        if len(pontuacao_anterior) == 0 :
            cargo = dias -faltas_a_descontar(ano,pessoa)
            funcao = dias - faltas_a_descontar(ano,pessoa)
            ue = dias - faltas_a_descontar(ano,pessoa)
        else:
            cargo = int(pontuacao_anterior[0].cargo_atrib) + dias - faltas_a_descontar(ano,pessoa)
            funcao = int(pontuacao_anterior[0].funcao_atrib) + dias - faltas_a_descontar(ano,pessoa)
            ue = int(pontuacao_anterior[0].ue_atrib) + dias - faltas_a_descontar(ano,pessoa)
             
    return cargo, funcao, ue


def gerar_pontuacao_anual_v2(ano,pessoa):
    pontuacao = Pontuacoes.objects.filter(pessoa=pessoa).filter(ano=ano-1).first()
    acumulado_funcao, acumulado_cargo, acumulado_ue = 0, 0, 0
    
    if pontuacao:
        acumulado_funcao, acumulado_cargo, acumulado_ue = pontuacao.funcao, pontuacao.cargo, pontuacao.ue
        
      
    funcao = acumular_dias(ano,pessoa.id,acumulado_funcao)
    cargo = acumular_dias(ano,pessoa.id,acumulado_cargo)
    ue = acumular_dias(ano,pessoa.id,acumulado_ue)
    
    return funcao, cargo, ue


def gerar_lancamento_em_memoria(data_lanc,qtd_dias):
    '''Atraves da data de lancamento e quantidade de dias gera um dicionario ano a ano com as devidas datas'''
    # Ex. anos[2020] = [(mes,dia,ano),(mes,dia,ano)], anos[2021]=[(mes, dia, ano)]
    anos = {}
    data = data_lanc

    for dia in range(0,qtd_dias):
        
        if data.year not in anos.keys():
            anos[data.year] = [data]
        
        else:
            anos[data.year].append(data)
        
        data += timedelta(days=1)
    
    return anos