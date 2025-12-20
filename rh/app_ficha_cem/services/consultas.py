from rh.app_ficha_cem.models import  Pessoas, Faltas_Pessoas
from rh.app_pontuacao.models import Pontuacoes
from .configuracoes import configurar_meses_v4, retornarNomeMes
from .calculos import gerar_pontuacao_anual_v2, data_util, contar_tipos_faltas
from .transformacoes import transformar_em_um_dicionario, formatar_cargo_disciplina
from datetime import timedelta

# recupera a pontuação do ano corrente 
def checar_existencia_pontuacao(ano, pessoa):
    status = True
    q2 = Pontuacoes.objects.filter(pessoa=pessoa)
    q3 = Pontuacoes.objects.filter(ano=ano)
    pontuacao = q2.intersection(q3)

    if pontuacao.count():
        status = False
    else:
        status = True

    return  status 

def consultar_anos_status(pessoa):
    anos, pessoa = listar_anos(pessoa)
    
    anos_status = {}
   
    for a in anos:
        status  = checar_existencia_pontuacao(a,pessoa)
        if status:
            status = 'Aberto'
        else:
            status = 'Fechado'
        anos_status[a] = status

    return anos_status,anos

def consultar_pontuacao(pessoa_id, ano,num=0):
    pontuacao = Pontuacoes.objects.filter(pessoa=pessoa_id).filter(ano=ano-num)
    
    if pontuacao.count():
        cargo = pontuacao[0].cargo
        funcao = pontuacao[0].funcao
        ue = pontuacao[0].ue
    else:
        cargo = 0
        funcao = 0
        ue = 0

    return funcao,cargo,ue


def buscar_informacoes_ficha_v2(pessoa_id, ano):
    anos, pessoa = listar_anos(pessoa_id)
    pessoa = Pessoas.objects.get(pk=pessoa_id)
    meses = configurar_meses_v4(ano,pessoa_id)
    funcao, cargo, ue  = gerar_pontuacao_anual_v2(ano,pessoa)
    funcao_a, cargo_a, ue_a = consultar_pontuacao(pessoa_id, ano, 1)
    ano_a = ano - 1
    meses_pontuacao = transformar_em_um_dicionario(funcao,cargo,ue)
    
    ano_st = consultar_anos_status(pessoa.id)
    ano_status = ano_st[0][ano]

    dias = []
    for dia in range(1,32):
        dias.append(dia)
   
    faltas = Faltas_Pessoas.objects.all().order_by('data').filter(data__year=ano).filter(pessoa=pessoa_id)
    admissao = pessoa.admissao
    saida = pessoa.saida


    

    des_cargo, disciplina = formatar_cargo_disciplina(pessoa.cargo)
 
    tipo_faltas=contar_tipos_faltas(faltas)
   
    data = ''

    for falta in faltas:
       
        data = falta.data
        
        for d in range(falta.qtd_dias):
              
            if d > 0:
                data = data + timedelta(days=1)

            # retorna as datas úteis se tipo da falta for P, caso contrário retorna a própria data
            data = data_util(data, falta.falta.tipo)

            mes = data.month
            dia = data.day - 1
            
            if mes == 1:
                meses['janeiro'][dia] = falta.falta.tipo
            elif mes == 2:
                meses['fevereiro'][dia] = falta.falta.tipo
            elif mes == 3:
                meses['março'][dia] = falta.falta.tipo
            elif mes == 4:
                meses['abril'][dia] = falta.falta.tipo
            elif mes == 5:
                meses['maio'][dia] = falta.falta.tipo
            elif mes == 6:
                meses['junho'][dia] = falta.falta.tipo
            elif mes == 7:
                meses['julho'][dia] = falta.falta.tipo
            elif mes == 8:
                meses['agosto'][dia] = falta.falta.tipo
            elif mes == 9:
                meses['setembro'][dia] = falta.falta.tipo
            elif mes == 10:
                meses['outubro'][dia] = falta.falta.tipo
            elif mes == 11:
                meses['novembro'][dia] = falta.falta.tipo
            elif mes == 12:
                meses['dezembro'][dia] = falta.falta.tipo


    faltas_mes_a_mes = faltas_por_mes_v2(meses)            
    
    pessoa.cpf = f'{pessoa.cpf[:3]}.{pessoa.cpf[3:6]}.{pessoa.cpf[6:9]}-{pessoa.cpf[-2:]}'
    
    if pessoa.efetivo:
        pessoa.efetivo='Sim'
    else:
        pessoa.efetivo='Não'

    contexto = {
        'ano_a':ano_a,
        'ano_status':ano_status,
        'meses': meses,
        'falta_por_mes': faltas_mes_a_mes,
        'ano': ano,
        'funcao': funcao,
        'cargo': cargo,
        'ue': ue,
        'des_cargo':des_cargo,
        'disciplina': disciplina,
        'funcao_a': funcao_a,
        'cargo_a': cargo_a,
        'ue_a': ue_a,
        'nome': pessoa.nome,
        'pessoa': pessoa,
        'dias': dias,
        'tp_faltas': tipo_faltas,
        'admissao':admissao,
        'saida':saida,
        'anos':anos,
        'meses_pontu': meses_pontuacao
        # 'pagesize':'A4'

    }
    
    print("Versão2", contexto)
    
    return contexto

# criação 25/12/2022
def buscar_informacoes_ficha_v3(pessoa_id, ano):
    anos, pessoa = listar_anos(pessoa_id)
    pessoa = Pessoas.objects.get(pk=pessoa_id)
    meses = configurar_meses_v4(ano,pessoa_id)
    funcao, cargo, ue  = gerar_pontuacao_anual_v2(ano,pessoa)
    funcao_a, cargo_a, ue_a = consultar_pontuacao(pessoa_id, ano, 1)
    ano_a = ano - 1
    meses_pontuacao = transformar_em_um_dicionario(funcao,cargo,ue)
    ano_st = consultar_anos_status(pessoa.id)
    ano_status = ano_st[0][ano]
    
    dias = []
    for dia in range(1,32):
        dias.append(dia)
   
    admissao = pessoa.admissao
    saida = pessoa.saida
    
    des_cargo, disciplina = formatar_cargo_disciplina(pessoa)
    tipo_faltas = retornar_preenchimento_tipos_falta(ano, pessoa_id, meses)
    faltas_mes_a_mes = faltas_por_mes_v2(meses)  

    linha = 0
    eventos_por_mes = []
    
    for k in faltas_mes_a_mes:
        eventos_por_mes.append(list(faltas_mes_a_mes[k].values()))
    

    # pega chaves de um mes qualquer que será a linha de eventos
    cabecalho_tp_faltas = list(faltas_mes_a_mes['janeiro'].keys())
    linha = 0
    for valor in meses.values():
        valor.extend(eventos_por_mes[linha])
        linha +=1
    
    linha = 0
    for mes, dias_do_mes in meses.items():
        for m, pontuacao in meses_pontuacao.items():
            if mes == m:
                dias_do_mes.extend(pontuacao)
   

    colunas_eventos = len(faltas_mes_a_mes['fevereiro'])
    colunas = range(len(meses['fevereiro'])-31-4 - colunas_eventos)
    colunas_pontuacao = range(len(meses['fevereiro'])-31-3)
    # print(faltas_mes_a_mes)          
    print(colunas_eventos)
    pessoa.cpf = f'{pessoa.cpf[:3]}.{pessoa.cpf[3:6]}.{pessoa.cpf[6:9]}-{pessoa.cpf[-2:]}'
    
    if pessoa.efetivo:
        pessoa.efetivo='Sim'
    else:
        pessoa.efetivo='Não'
    

    contexto = {
        'ano_a':ano_a,
        'ano_status':ano_status,
        'meses': meses,
        'falta_por_mes': faltas_mes_a_mes,
        'ano': ano,
        'funcao': funcao,
        'cargo': cargo,
        'ue': ue,
        'des_cargo':des_cargo,
        'disciplina': disciplina,
        'funcao_a': funcao_a,
        'cargo_a': cargo_a,
        'ue_a': ue_a,
        'nome': pessoa.nome,
        'pessoa': pessoa,
        'dias': dias,
        'tp_faltas': tipo_faltas,
        'admissao':admissao,
        'saida':saida,
        'anos':anos,
        'meses_pontu': meses_pontuacao,
        'cabecalho_tf': cabecalho_tp_faltas,
        'colunas': colunas,
        'colunas_eventos': colunas_eventos,
        'colunas_pontuacao': colunas_pontuacao
        # 'pagesize':'A4'

    }

    # colocar em ordem decrescente
    contexto['anos'] = sorted(contexto['anos'], reverse=True)

    print("Versão3", contexto)
    return contexto

# preencher tipos_faltas
def retornar_preenchimento_tipos_falta(ano, pessoa_id, meses):
    faltas = Faltas_Pessoas.objects.filter(data__year=ano).filter(pessoa=pessoa_id).order_by('data')
    tipo_faltas=contar_tipos_faltas(faltas)
    data = ''
    for falta in faltas:
       
        data = falta.data
        
        for d in range(falta.qtd_dias):
              
            if d > 0:
                data = data + timedelta(days=1)

            # retorna as datas úteis se tipo da falta for P, caso contrário retorna a própria data
            data = data_util(data, falta.falta.tipo)

            mes = data.month
            dia = data.day - 1
        
           
            # preenche onde acontece a falta
            meses[retornarNomeMes(mes)][dia] = falta.falta.tipo
    
    return tipo_faltas

# listar anos de uma determinada pessoa
def listar_anos(pessoa_id):
    anos = []
    pessoa_faltas = Faltas_Pessoas.objects.all()
    pessoa = Pessoas.objects.get(pk=pessoa_id)

    for i in pessoa_faltas:
        if i.data.year not in anos and i.pessoa.id == pessoa_id:
            anos.append(i.data.year)

    return anos[-5:], pessoa


def verificar_status_ano(ano, pessoa_id):
    pontuacao = Pontuacoes.objects.filter(pessoa=pessoa_id).filter(ano=ano)
    ano_fechado = True

    if pontuacao.count() == 0:
        ano_fechado = False
    
    return ano_fechado

def verificar_data_saida(data_lancamento,pessoa_id):
    pessoa = Pessoas.objects.get(pk=pessoa_id)
   
    ativo = pessoa.saida 
    if ativo is not None:
        if data_lancamento <= ativo:
            return True
        else:
            return False
    else:
        return True


    
def faltas_por_mes_v2(meses):
    '''Guarda dados de comparecimento e todos os tipos de faltas que ocorreram e suas quantidades, uniforme a todos os meses'''
    faltas_por_mes = {}
    faltas_por_mes_n = {}

    for k,v in meses.items():
        for i in v:
            if i != '-':
                faltas_por_mes_n[i] = 0
        
    for k,v in meses.items():
        if k not in faltas_por_mes:
            faltas_por_mes[k] = faltas_por_mes_n.copy()
        for i in v:
            if i != '-':
                faltas_por_mes[k][i] += 1
               
    return faltas_por_mes
    
def faltas_por_mes(meses):
    '''Guarda as faltas referentes somente aos meses em que elas aparecem, não guarda armazenamentos'''
    faltas_por_mes = {}
    for k,v in meses.items():
        if k not in faltas_por_mes:
            faltas_por_mes[k] = {}
       
        for i in v:
            if i != 'C' and i != ' ':
             
                if i not in faltas_por_mes[k]:
                    faltas_por_mes[k][i] = 1
                else:
                    faltas_por_mes[k][i] += 1
    return faltas_por_mes