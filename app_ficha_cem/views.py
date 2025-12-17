# Create your views here.
from datetime import date, datetime, timedelta
from functools import partial
from io import BytesIO

from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.defaulttags import register
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import (Image, Paragraph, SimpleDocTemplate, Spacer,
                                Table, TableStyle)

from app_pessoa.models import Pessoas
from utilitarios.utilitarios import retornarNomeMes, retornar_meses

from .forms import (FaltaPesquisaForm, FaltaPesquisaFormGeral,
                    FiltroRelatorioDescritivoForm, formularioLF,
                    formularioPontuacao)
from .models import Cargos, Faltas, Faltas_Pessoas, Pontuacoes




# função recursiva que determina se a data é útil (excluindo sábado e domingo) para o tipo P, senão retorna própria data
def data_util(data, tp='P'):
    
    if tp == 'P':
        if (data.weekday() != 6 and data.weekday() != 5):
            return data
        data = data + timedelta(days=1)
        return data_util(data)
    return data

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


def verificar_status_ano(ano, pessoa_id):
    pontuacao = Pontuacoes.objects.filter(pessoa=pessoa_id).filter(ano=ano)
    ano_fechado = True

    if pontuacao.count() == 0:
        ano_fechado = False
    
    return ano_fechado


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


def verificar_ano_saida(pessoa_id):
    pessoa = Pessoas.objects.get(pk=pessoa_id)
   
    ativo = pessoa.saida 
    if ativo is not None:
        ano = pessoa.admissao.year
        if ano >= ativo.year:
            return True
        else:
            return False
    else:
        return True


# fazer o lançamento de faltas para determinada pessoa
def pessoas_faltas(request, pessoa_id):

    pessoa = Pessoas.objects.get(pk=pessoa_id)
    pessoa_falta = Faltas_Pessoas.objects.filter(pessoa=pessoa).order_by('data')[:30]
    admissao = pessoa.admissao
    saida = pessoa.saida 
    data_lancamento = 0

    # ideia hora/aula
    ha = {}
    valor_ha = []
    for lancamento in pessoa_falta:
        if lancamento.falta.tipo == 'HA':
            valor_ha.append(lancamento.qtd_dias)
            ha[lancamento.id] = valor_ha.copy()
            
    for k, v in ha.items():
        ha[k] = sum(v)

    print(ha, '===')
    
    if request.method == 'POST':
        # instância do formulário para pegar dados
        form = formularioLF(request.POST)

        # pegar valores do formulário
        qtd_dias = int(form.data['qtd_dias'])
        data_lancamento = form['data'].value()
        falta = Faltas.objects.get(pk=form['falta'].value())

        
       
        data_lancamento = datetime.strptime(data_lancamento, '%Y-%m-%d').date()

        # criar intervalos de lançamentos na memória e dividir por ano (ano é chave)
        dia_mes_ano = gerar_lancamento_em_memoria(data_lancamento, qtd_dias)
       
        # verifica se os dados preenchidos são válidos
        # verifica se existe faltas naquele intervalo
        # conflito, ano_fechado = lancar_falta(data_lancamento, qtd_dias ,pessoa_id)
        conflito = lancar_falta(data_lancamento, qtd_dias, pessoa_id)
        ano_fechado = verificar_status_ano(data_lancamento.year, pessoa_id)
        
        ativo = verificar_data_saida(data_lancamento, pessoa_id)
        print(form)
        if form.is_valid():
            
            if  data_lancamento >= admissao and ativo:
                
                if conflito:
                    if not ano_fechado:
                        # navega entre as chaves (ano)
                        for k in dia_mes_ano.keys():
                            qtd_dias = len(dia_mes_ano[k]) # quantos dias existem dentro da chave ano
                            data_lancamento = dia_mes_ano[k][0] # pega o primeiro dia do lançamento e depois o primeiro dia do ano

                            # cria objeto com os novos dados
                            novoObj = Faltas_Pessoas(pessoa=pessoa, data=data_lancamento, qtd_dias=qtd_dias, falta=falta)
                             
                            # salva o objeto
                            novoObj.save()
                
                        messages.success(request,"Falta registrada!")
                        return redirect('lancarfalta',pessoa_id)
                    else:
                        messages.error(request,f"Ano {data_lancamento.year} Fechado! Abrir se deseja efetuar lançamentos!",'danger')

                else:
                    messages.error(request,"Não foi possível registrar a falta! Pode existir conflito de datas!",'danger')
            else:
            
                if not ativo:
                    messages.warning(request,f"Precisa ser uma data válida!  Data Admissão: {admissao.strftime('%d/%m/%Y')} Data Saída: {saida.strftime('%d/%m/%Y')}")
                else:
                    messages.warning(request,f"Precisa ser uma data válida!  Data Admissão: {admissao.strftime('%d/%m/%Y')}")
        else:
            messages.error(request,"Formulário Inválido!",'danger')

    else:
            
        form = formularioLF(initial={'pessoa':pessoa})
    return render(request,'template/lancar_falta.html', {'form':form, 'pessoa':pessoa, 'faltas':pessoa_falta})


def excluir_pessoas_faltas(request, pessoa_id, lancamento_id):

    lancamento = Faltas_Pessoas.objects.filter(pk=lancamento_id)
    pessoa = Pessoas.objects.get(pk=pessoa_id)
    pessoa_falta = Faltas_Pessoas.objects.filter(pessoa=pessoa).order_by('data')[:30]

    if request.method == 'GET':
        lancamento.delete()    
        messages.success(request,"Lançamento Apagado!")
        return redirect('lancarfalta',pessoa_id)
    else:
        form = formularioPontuacao(initial={'pessoa':pessoa})
    
    return render(request,'template/lancar_falta.html', {'form':form, 'pessoa':pessoa, 'faltas':pessoa_falta})
        
        
# listar anos de uma determinada pessoa
def listar_anos(pessoa_id):
    anos = []
    pessoa_faltas = Faltas_Pessoas.objects.all()
    pessoa = Pessoas.objects.get(pk=pessoa_id)

    for i in pessoa_faltas:
        if i.data.year not in anos and i.pessoa.id == pessoa_id:
            anos.append(i.data.year)

    return anos[-5:], pessoa


def listar_ficha(request, pessoa_id):
    anos, pessoa = listar_anos(pessoa_id)
    anos_status = {}
    for ano in anos:
        status  = checar_existencia_pontuacao(ano,pessoa)
        if status:
            status = 'Aberto'
        else:
            status = 'Fechado'
        anos_status[ano] = status

    # ordem decrescente de ano
    anos_status = dict(sorted(anos_status.items(), key=lambda item: item[0], reverse=True))
  
    return render(request,'template/listar_ficha_v2.html',{'anos':anos_status, 'pessoa':pessoa})

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

from django.db.models import Sum

############################# Filtros #########################

# 
def gerar_requerimento_abono_pdf(request, servidor_id, ano):
    servidor = get_object_or_404(Pessoas, pk=servidor_id)
    faltas = Faltas_Pessoas.objects.filter(pessoa=servidor, data__year=ano)

    faltas_justificadas = []
    faltas_injustificadas = []
    faltas_abonadas = []
    licencas_saude = []

    for falta in faltas:
        dias = getattr(falta, 'qtd_dias', 1)
        tipo = falta.falta.tipo  # AM, AO, FJ, I, AB, etc.

        # Se tiver mais de 3 dias e for do tipo justificável, vai para Licença Saúde
        if dias > 3 and tipo in ['AM', 'AO', 'J']:
            licencas_saude.append(falta)
        else:
            if tipo in ['AM', 'AO', 'FJ','LM', 'LN']:
                faltas_justificadas.append(falta)
            elif tipo == 'I':
                faltas_injustificadas.append(falta)
            elif tipo == 'AB':
                faltas_abonadas.append(falta)

    categorias = {
        'FALTAS JUSTIFICADAS': faltas_justificadas,
        'FALTAS INJUSTIFICADAS': faltas_injustificadas,
        'FALTAS ABONADAS': faltas_abonadas,
        'LICENÇAS SAÚDE': licencas_saude,
    }

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Relatorio_{servidor.nome}.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm,
    )

    elements = []

    # --- Estilos com Helvetica (Arial-like) ---
    estilo_centro = ParagraphStyle(name='centro', alignment=1, fontName='Helvetica', fontSize=11)
    estilo_negrito = ParagraphStyle(name='negrito', alignment=1, fontName='Helvetica-Bold', fontSize=12, spaceBefore=6, spaceAfter=6)
    estilo_normal = ParagraphStyle(name='normal', fontName='Helvetica', fontSize=11)
    estilo_cabecalho = ParagraphStyle(name='cabecalho', fontName='Helvetica', fontSize=10, alignment=1, leading=12)
    estilo_celula_texto = ParagraphStyle(name='celula_texto', fontName='Helvetica', fontSize=10, alignment=0, leading=12)
    estilo_celula_centro = ParagraphStyle(name='celula_centro', fontName='Helvetica', fontSize=10, alignment=1, leading=12)

    # Cabeçalho
    elements.append(Paragraph("<b>Prefeitura Municipal de Orlândia</b>", estilo_negrito))
    elements.append(Paragraph("REQUERIMENTO ÚNICO ANUAL DE ABONO / JUSTIFICAÇÃO DE FALTAS", estilo_centro))
    elements.append(Paragraph(f"<b>Ano {ano}</b>", estilo_centro))
    elements.append(Spacer(1, 12))

    if "PEB" in servidor.cargo.cargo:
        funcionario = "PROFESSOR(A)"
    else:
        funcionario = "FUNCIONÁRIO(A)"

    # Tabela de dados do servidor
    tabela_dados = [
        ["UNIDADE ESCOLAR:", "EMEB Profª Victória Olivito Nonino"],
        [f"NOME DO(A) {funcionario}:", servidor.nome],
        ["CARGO / FUNÇÃO:", servidor.cargo],
        ["MATRÍCULA:", servidor.id],
    ]
    largura_total = 15.5 * cm
    colunas_info = [5.5 * cm, largura_total - 5.5 * cm]
    table_info = Table(tabela_dados, colWidths=colunas_info)
    table_info.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(table_info)
    elements.append(Spacer(1, 14))

    # Tabelas das categorias
    for titulo, lista in categorias.items():
        elements.append(Paragraph(f"<b>{titulo}</b>", estilo_negrito))
        elements.append(Spacer(1, 6))

        if lista:
            header = [
                Paragraph("<b>Nº</b>", estilo_celula_centro),
                Paragraph("<b>Data da Falta</b>", estilo_celula_centro),
                Paragraph("<b>Assinatura do Requerente</b>", estilo_cabecalho),
                Paragraph("<b>Desp. Def./Indef.</b>", estilo_cabecalho),
                Paragraph("<b>Superior Imediato</b>", estilo_celula_centro),
            ]
            dados = [header]
            colunas = [1.2 * cm, 3 * cm, 6.5 * cm, 2.5 * cm, 2.3 * cm]

            for i, falta in enumerate(lista, 1):
                # Determina o período da falta usando qtd_dias
                if getattr(falta, 'qtd_dias', 1) > 1:
                    data_fim = falta.data + timedelta(days=falta.qtd_dias - 1)
                    data_texto = f"{falta.data.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
                else:
                    data_texto = falta.data.strftime("%d/%m/%Y")

                row = [
                    Paragraph(f"{i}ª", estilo_celula_centro),
                    Paragraph(data_texto, estilo_celula_centro),
                    Paragraph("", estilo_celula_texto),
                    Paragraph("", estilo_celula_texto),
                    Paragraph("", estilo_celula_texto),
                ]
                dados.append(row)
            
        else:
            dados = [[Paragraph("Sem ocorrências", estilo_celula_centro)]]
            colunas = [largura_total]

        tabela = Table(dados, colWidths=colunas)
        estilo = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]

        if not lista:
            estilo += [
                ('SPAN', (0, 0), (-1, 0)),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]
        else:
            estilo += [
                ('ALIGN', (0, 0), (1, -1), 'CENTER'),
                ('ALIGN', (2, 0), (4, -1), 'LEFT'),
            ]

        tabela.setStyle(TableStyle(estilo))
        elements.append(tabela)
        elements.append(Spacer(1, 16))

    doc.title = f"Abono {servidor.nome}"
    doc.build(elements)
    return response

def relatorio_faltas_geral(request):
    form = FaltaPesquisaFormGeral(request.GET or None)
    resultados = []
    totais_por_tipo = []
    total_geral = 0

    if form.is_valid():
        data_inicio = form.cleaned_data['data_inicio']
        data_fim = form.cleaned_data['data_fim']
        faltas_selecionadas = form.cleaned_data['falta']
        cargos_selecionados = form.cleaned_data['cargo']
        efetivo = form.cleaned_data['efetivo']
        ativo = form.cleaned_data['ativo']

        faltas = Faltas_Pessoas.objects.select_related('pessoa', 'falta').filter(
            data__range=(data_inicio, data_fim)
        )

        if faltas_selecionadas:
            faltas = faltas.filter(falta__in=faltas_selecionadas)

        if cargos_selecionados:
            faltas = faltas.filter(pessoa__cargo__in=cargos_selecionados)

        if efetivo == 'sim':
            faltas = faltas.filter(pessoa__efetivo=True)
        elif efetivo == 'nao':
            faltas = faltas.filter(pessoa__efetivo=False)

        if ativo == 'sim':
            faltas = faltas.filter(pessoa__ativo=True)
        elif ativo == 'nao':
            faltas = faltas.filter(pessoa__ativo=False)

        resultados = faltas.order_by('data')

        totais_por_tipo = (
            faltas.values('falta__descricao')
            .annotate(total_dias=Sum('qtd_dias'))
            .order_by('falta__descricao')
        )

        total_geral = faltas.aggregate(soma=Sum('qtd_dias'))['soma'] or 0

    return render(request, 'template/relatorio_geral.html', {
        'form': form,
        'resultados': resultados,
        'totais_por_tipo': list(totais_por_tipo),
        'total_geral': total_geral,
    })

def relatorio_faltas(request, pessoa_id):
    pessoa = get_object_or_404(Pessoas, id=pessoa_id)
    form = FaltaPesquisaForm(request.GET or None)
    resultados = []
    totais_por_tipo = []
    total_geral = 0

    if form.is_valid():
        data_inicio = form.cleaned_data['data_inicio']
        data_fim = form.cleaned_data['data_fim']
        faltas_selecionadas = form.cleaned_data['falta']

        filtros_comuns = {
            'pessoa': pessoa,
            'data__range': (data_inicio, data_fim),
        }

        if faltas_selecionadas:
            filtros_comuns['falta__in'] = faltas_selecionadas

        faltas_queryset = Faltas_Pessoas.objects.filter(**filtros_comuns)

        resultados = faltas_queryset.select_related('pessoa', 'falta').order_by('data')

        totais_por_tipo = (
            faltas_queryset
            .values('falta__descricao')
            .annotate(total_dias=Sum('qtd_dias'))
            .order_by('falta__descricao')
        )

        total_geral = faltas_queryset.aggregate(soma=Sum('qtd_dias'))['soma'] or 0

    return render(request, 'template/relatorio.html', {
        'form': form,
        'pessoa': pessoa,
        'resultados': resultados,
        'totais_por_tipo': totais_por_tipo,
        'total_geral': total_geral,
    })



def relatorio_faltas_descritivo(request):
    form = FiltroRelatorioDescritivoForm(request.GET or None)
    dados_agrupados = {}
    total_funcionarios = 0

    if form.is_valid():
        data_inicial = form.cleaned_data['data_inicial']
        data_final = form.cleaned_data['data_final']
        efetivo = form.cleaned_data['efetivo']
        publico = form.cleaned_data['func_publico']
        print(efetivo)
        
        if efetivo == 'sim':
            efetivo = True
        elif efetivo == 'nao':
            efetivo = False
       

        if publico == 'sim':
            publico = True
        else:
            publico  = False

        print(efetivo)

        if efetivo == 'ambos':
            registros = (Faltas_Pessoas.objects
                     .filter(data__range=(data_inicial, data_final))
                     .select_related('pessoa', 'falta')
                     .filter(pessoa__func_publico = publico)
                     .order_by('pessoa__nome','falta__descricao','data'))
        
        else:
        
            registros = (Faltas_Pessoas.objects
                     .filter(data__range=(data_inicial, data_final))
                     .select_related('pessoa', 'falta')
                     .filter(pessoa__efetivo = efetivo)
                     .filter(pessoa__func_publico = publico)
                     .order_by('pessoa__nome','falta__descricao','data'))
        
        for registro in registros:
            pessoa = registro.pessoa
            if pessoa.id not in dados_agrupados:
                dados_agrupados[pessoa.id] = {
                    'matricula': pessoa.id,
                    'nome': pessoa.nome,
                    'faltas': []
                }
            dados_agrupados[pessoa.id]['faltas'].append({
                'data': registro.data,
                'tipo': registro.falta.descricao,
                'qtd_dias': registro.qtd_dias
            })
        
        total_funcionarios = len(dados_agrupados)

    return render(request, 'template/relatorio_faltas_descritivo.html', {
        'form': form,
        'dados': dados_agrupados,
        'total_funcionarios': total_funcionarios
    })



def relatorio_faltas_descritivo_pdf(request):

    
    data_inicio_str = request.GET.get('data_inicio')
    data_fim_str = request.GET.get('data_fim')
    efetivo = request.GET.get('efetivo')
    publico = request.GET.get('publico')
    titulo = ""

    if not data_inicio_str or not data_fim_str:
        return HttpResponse("Informe a data inicial e final.", status=400)

    try:
        data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d')
        data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d')
    except ValueError:
        return HttpResponse("Formato de data inválido. Use YYYY-MM-DD.", status=400)

    if efetivo == 'sim':
        efetivo = True
        titulo = "Efetivos"

    elif efetivo == 'nao':
        efetivo = False
        titulo = "Contratados"

    if publico == 'sim':
        publico = True


    else:
        publico  = False
        titulo = "Outros Funcionários"

    if efetivo == 'ambos':
        faltas_qs = (Faltas_Pessoas.objects
                     .filter(data__range=(data_inicio, data_fim))
                     .select_related('pessoa', 'falta')
                     .filter(pessoa__func_publico = publico)
                     .order_by('pessoa__nome','falta__descricao','data'))
        titulo = "Efetivos e Contratados"
        
    else:
        
        faltas_qs = (Faltas_Pessoas.objects
                     .filter(data__range=(data_inicio, data_fim))
                     .select_related('pessoa', 'falta')
                     .filter(pessoa__efetivo = efetivo)
                     .filter(pessoa__func_publico = publico)
                     .order_by('pessoa__nome','falta__descricao','data'))
 

    pessoas_com_falta = {}
    for falta in faltas_qs:
        pessoa_id = falta.pessoa.id
        if pessoa_id not in pessoas_com_falta:

            pessoas_com_falta[pessoa_id] = {
                'matricula': falta.pessoa.id,
                'nome': falta.pessoa.nome,
                'cargo': falta.pessoa.cargo,
                'efetivo': "Efetivo" if falta.pessoa.efetivo else  "Contratado",
                'faltas': []
            }
        pessoas_com_falta[pessoa_id]['faltas'].append(falta)

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margem_x = 2 * cm
    y = height - 2 * cm

    def desenhar_cabecalho():
        p.setFont("Helvetica-Bold", 14)
        p.drawCentredString(width / 2, y, f"Relatório de Faltas - {titulo}")
        y_text = y - 1 * cm
        p.setFont("Helvetica", 10)
        p.drawCentredString(width / 2, y_text, f"Período: {data_inicio.strftime('%d/%m/%Y')} até {data_fim.strftime('%d/%m/%Y')}")
        return y_text - 1 * cm

    def nova_pagina():
        nonlocal y
        p.showPage()
        y = height - 2 * cm
        y = desenhar_cabecalho()
        return y

    # Desenha o cabeçalho inicial
    y = desenhar_cabecalho()

    total_funcionarios = len(pessoas_com_falta)
    p.setFont("Helvetica", 9)

    for pessoa_data in pessoas_com_falta.values():
        if y <= 3 * cm:
            y = nova_pagina()

        # Cabeçalho de pessoa
        p.setFont("Helvetica-Bold", 10)
        p.setFillColor(colors.darkblue)
        p.drawString(margem_x, y, f"{pessoa_data['matricula']} - {pessoa_data['nome']} ({pessoa_data['cargo']} : {pessoa_data['efetivo']})")
        p.setFillColor(colors.black)
        y -= 0.8 * cm

        # Tabela de faltas
        p.setFont("Helvetica", 9)
        header = ["Data", "Tipo", "Dias"]
        col_widths = [3.5 * cm, 8 * cm, 2 * cm]
        p.setFillColor(colors.grey)
        p.rect(margem_x, y, sum(col_widths), 0.5 * cm, fill=True, stroke=False)
        p.setFillColor(colors.white)
        p.drawString(margem_x + 0.2 * cm, y + 0.15 * cm, header[0])
        p.drawString(margem_x + col_widths[0] + 0.2 * cm, y + 0.15 * cm, header[1])
        p.drawString(margem_x + col_widths[0] + col_widths[1] + 0.2 * cm, y + 0.15 * cm, header[2])
        y -= 0.5 * cm

        alternar = False
        for falta in pessoa_data['faltas']:
            if y <= 3 * cm:
                y = nova_pagina()
                p.setFont("Helvetica-Bold", 10)
                p.drawString(margem_x, y, f"{pessoa_data['matricula']} - {pessoa_data['nome']} ({pessoa_data['cargo']} : {pessoa_data['efetivo']})")
                y -= 0.8 * cm

                # Redesenhar cabeçalho da tabela na nova página
                p.setFont("Helvetica", 9)
                p.setFillColor(colors.grey)
                p.rect(margem_x, y, sum(col_widths), 0.5 * cm, fill=True, stroke=False)
                p.setFillColor(colors.white)
                p.drawString(margem_x + 0.2 * cm, y + 0.15 * cm, header[0])
                p.drawString(margem_x + col_widths[0] + 0.2 * cm, y + 0.15 * cm, header[1])
                p.drawString(margem_x + col_widths[0] + col_widths[1] + 0.2 * cm, y + 0.15 * cm, header[2])
                y -= 0.5 * cm

            cor_fundo = colors.whitesmoke if alternar else colors.lightgrey
            p.setFillColor(cor_fundo)
            p.rect(margem_x, y, sum(col_widths), 0.4 * cm, fill=True, stroke=False)
            p.setFillColor(colors.black)
            p.setFont("Helvetica", 9)
            p.drawString(margem_x + 0.2 * cm, y + 0.1 * cm, falta.data.strftime('%d/%m/%Y'))
            p.drawString(margem_x + col_widths[0] + 0.2 * cm, y + 0.1 * cm, falta.falta.descricao)
            p.drawString(margem_x + col_widths[0] + col_widths[1] + 0.2 * cm, y + 0.1 * cm, str(falta.qtd_dias))
            y -= 0.4 * cm
            alternar = not alternar

        y -= 0.4 * cm

    if y <= 3 * cm:
        y = nova_pagina()

    # Total no final
    p.setFont("Helvetica-Bold", 11)
    p.drawString(margem_x, y, f"Total de funcionários com faltas: {total_funcionarios}")

    p.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="relatorio_faltas.pdf"'
    return response

###### Fim Filtros ###########

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

def transformar_em_um_dicionario(funcao,cargo,ue):
    
    meses_pontuacao = {}
    cargo_lst = []
    funcao_lst = []
    ue_lst = []
    for v in cargo.values():
        cargo_lst.append(v)
    
    for v in funcao.values():
        funcao_lst.append(v)

    for v in ue.values():
        ue_lst.append(v)

    i = 0
    for k, v in cargo.items():
        meses_pontuacao[k] = [funcao_lst[i],cargo_lst[i], ue_lst[i]]
        i = i + 1

    return meses_pontuacao

def buscar_informacoes_ficha_v2(pessoa_id, ano):
    anos, pessoa = listar_anos(pessoa_id)
    pessoa = Pessoas.objects.get(pk=pessoa_id)
    meses = configurar_meses_v4(ano,pessoa_id)
    funcao, cargo, ue  = gerar_pontuacao_anual_v2(ano,pessoa)
    funcao_a, cargo_a, ue_a = consultar_pontuacao(pessoa_id, ano, 1)
    ano_a = ano - 1
    meses_pontuacao = transformar_em_um_dicionario(funcao,cargo,ue)
    
    print(meses,'na ficha')
    ano_st = consultar_anos_status(pessoa.id)
    ano_status = ano_st[0][ano]

    dias = []
    for dia in range(1,32):
        dias.append(dia)
   
    faltas = Faltas_Pessoas.objects.all().order_by('data').filter(data__year=ano).filter(pessoa=pessoa_id)
    admissao = pessoa.admissao
    saida = pessoa.saida

    conta = 0
    for l in str(pessoa.cargo):
        if l == '-':
            conta +=1

    if conta > 1:
        cargo_disciplina = str(pessoa.cargo).replace('-','')
        cargo_disciplina = cargo_disciplina + ' - N/A'
        cargo_disciplina = tuple(cargo_disciplina.split('-'))
    elif conta == 0:
        cargo_disciplina = str(pessoa.cargo) + ' - N/A'
        cargo_disciplina = tuple(cargo_disciplina.split('-'))
    else:
        cargo_disciplina = tuple(str(pessoa.cargo).split('-'))

    des_cargo, disciplina = cargo_disciplina
 
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
                meses['marco'][dia] = falta.falta.tipo
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

def formatar_cargo_disciplina(pessoa):

    cargo = str(pessoa.cargo)
    if '-' in cargo:
        cargo_disciplina = tuple(cargo.split('-'))
    else:
        cargo_disciplina = cargo + '-N/A'
        cargo_disciplina = tuple(cargo_disciplina.split('-'))

    return cargo_disciplina

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

    
    return contexto

def gerar_ficha(request, pessoa_id, ano):
    
    contexto = buscar_informacoes_ficha_v3(pessoa_id, ano)
    return render(request,'template/ficha_cem_v2.html', {'contexto':contexto})

def index(request):
    
    return render(request,'template/index.html')

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

def contar_dias(data_inicial, data_final):
    dias = (data_final - data_inicial ).days + 1

    return dias

def gerar_pontuacao_atribuicao(ano,pessoa, tipo='c'):
    '''a - ano anterior, c - ano corrente '''

    data_bas_ini = datetime.strptime(f'{ano-1}-11-01','%Y-%m-%d',).date()
    data_bas_fim = datetime.strptime(f'{ano}-10-31','%Y-%m-%d').date()

    if pessoa.admissao > data_bas_ini:
        data_bas_ini = pessoa.admissao

    dias = contar_dias(data_bas_ini, data_bas_fim)
    
    # q1 = PontuacoesAtribuicoes.objects.filter(ano=ano-1) # ano anterior
    # q2 = PontuacoesAtribuicoes.objects.filter(pessoa=pessoa)

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

# insere a chave dentro da lista 16/04/2025
def inserir_chave(dicionario, chave):
    for k,v in dicionario[chave].items():
        v.insert(0,k)
        
def pdf_v3(request, pessoa_id, ano):
    from io import BytesIO

    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.platypus import (Paragraph, SimpleDocTemplate, Table,
                                    TableStyle)
    
   
    
    contexto = buscar_informacoes_ficha_v2(pessoa_id, ano)

   
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, 
                            pagesize=landscape(A4), 
                            rightMargin=30, 
                            leftMargin=30, 
                            topMargin=30,
                            bottomMargin=18)
   
   

    # cria informações para a primeira linha da tabela
    mes_dias = ["Mês/Dia"]
    for i in range(1,32):
        mes_dias.append(i)
 
    # insere a chave dentro da lista dos meses na posição 0. Ex ['janeiro','C','C'...]
    inserir_chave(contexto, "meses")

    # insere no dicionario faltas na posição 0 a sigla da falta Ex 'contexto['FJ']'=['FJ','FALTA JUSTIFICADA',10]
    inserir_chave(contexto, "tp_faltas")

   
    # cria lista com os valores não a chave
    data_tp_falta = [tp for tp in contexto['tp_faltas'].values()]
    
    # cria lista com os valores dos meses 
    data_frequencia = [m for m in contexto['meses'].values()]

    # dentro dessa lista insere a lista mes_dias
    data_frequencia.insert(0, mes_dias)

    faltas_mes_a_mes = contexto['falta_por_mes']
    linha = 0
    eventos_por_mes = []
    
    # dicionarios aninhados com os meses dentro dos meses os tipos de eventos e a quantidade 17/04/2025
    for k in faltas_mes_a_mes:
        eventos_por_mes.append(list(faltas_mes_a_mes[k].values()))

    # pega chaves de um mes qualquer que será a linha de eventos
    eventos_por_mes.insert(0,list(contexto['falta_por_mes']['janeiro'].keys()))
    
    # extend a tabela frequencia com informação dos eventos
    for i in range(0,len(data_frequencia)):
        data_frequencia[i].extend(eventos_por_mes[i])
    
    
  
    brancos = len(contexto['tp_faltas'])
    brancos += 33
    linha = [' '] * brancos
    linha2 = [' '] * brancos
    
    data_frequencia.insert(1,linha)
    data_frequencia.insert(0,linha2)

    data_frequencia[0].extend(['Tempos'])
    data_frequencia[1].extend(['Função','Cargo','Unidade'])
    data_frequencia[2].extend([contexto['funcao_a'],contexto['cargo_a'],contexto['ue_a']])
    
    
    # transforma valores do dicionario em listas
    cargo_anual = list(contexto['cargo'].values())
    funcao_anual = list(contexto['funcao'].values())
    ue_anual = list(contexto['ue'].values())
    

    # data_frequencia.extend(cargo)
    inicio_linha = 3
    for i in range(12):
        data_frequencia[inicio_linha].extend([funcao_anual[i],cargo_anual[i],ue_anual[i]])
        inicio_linha += 1
   
    # aprender melhores tamanhos para configurar
    tamanho_fonte = 9
    qtd_eventos = len(contexto['tp_faltas'])
    fator_d = round(tamanho_fonte  / qtd_eventos, 3) 
    fator_i = round(tamanho_fonte  / qtd_eventos) 
    fator_d = '0.' + str(fator_d).split('.')[1]
    fator_d = float(fator_d)
    if   qtd_eventos > fator_i:
        tamanho_fonte = round(fator_d * tamanho_fonte )**2 * fator_i
    else:
        tamanho_fonte = 12
    
    

    print('Fator',fator_d)
    print('Fator',fator_i)


    # cria estilo 
    style_table_corpo = TableStyle([('GRID',(0,0),(-1,-1), 0.5, colors.black),
                            ('LEFTPADDING',(0,0),(-1,-1),2),
                            ('TOPPADDING',(0,0),(-1,-1),2),
                            ('BOTTOMPADDING',(0,0),(-1,-1),2),
                            ('RIGHTPADDING',(0,0),(-1,-1),2),
                            ('ALIGN',(0,0),(-1,-1),'CENTER'),
                            ('FONTSIZE',(0,0), (-1,-1),tamanho_fonte), 
                            ('SPAN',(-3,0),(-1,0)),
                            ('SPAN',(1,2),(31,2))          
                            ], spaceBefore=20)

    # cria tabela com as informações de data_faltas
    t_frequencia = Table(data_frequencia, hAlign='CENTER',)

    
    # aplica estilo diferente conforme a condição, ou seja, as faltas ficam com cor de background
    for row, values in enumerate(data_frequencia):
       for column, value in enumerate(values):
        #    print(column, value)
           if value in contexto['tp_faltas']:
               style_table_corpo.add('BACKGROUND',(column,row),(column,row),colors.lightblue)

    t_frequencia.setStyle(style_table_corpo)

    t_tipos = Table(data_tp_falta, style=[('GRID',(0,0),(-1,-1), 0.5, colors.black),
                            ('ALIGN',(0,0),(-1,-1),'CENTER'),
                            ('FONTSIZE',(0,0), (-1,-1),7.5),
                            ('LEFTPADDING',(0,0),(-1,-1),1),
                            ('TOPPADDING',(0,0),(-1,-1),1),
                            ('BOTTOMPADDING',(0,0),(-1,-1),1),
                            ('RIGHTPADDING',(0,0),(-1,-1),1),
                            ], hAlign='LEFT')

    styles = getSampleStyleSheet()
    
    styleH = ParagraphStyle('Cabeçalho',
                            fontSize=20,
                            parent=styles['Heading1'],
                            alignment=1,
                            spaceAfter=14)
    
    styleB = ParagraphStyle('Corpo',
                        spaceAfter=14
                    ) 
    
    styleAss = ParagraphStyle('Assinatura',
                        alignment=1,
            
                    ) 

    styleAssTrac =  ParagraphStyle('AssinaturaTrac',
                        alignment=1,
                        spaceBefore=20
            
                    ) 

    stylePessoa = ParagraphStyle('Pessoa',
                        # alignment=0,
                        spaceAfter=4
                        
                    ) 
    elementos = []
    # elements.append(Paragraph('<para><img src="https://www.orlandia.sp.gov.br/novo/wp-content/uploads/2017/01/brasaoorlandia.png" width="40" height="40"/> </para>'))
    elementos.append(Paragraph(f"<strong>Ficha Frequência - Ano</strong>:{contexto['ano']}", styleH))
    # elements.append(Paragraph(f"<strong>Nome</strong>: {contexto['pessoa'].nome}  RM: {contexto['pessoa'].id}", styleB))
    
    saida = '' if contexto['pessoa'].saida == None else  contexto['pessoa'].saida.strftime('%d/%m/%Y')

    data_pessoa = [
        [Paragraph(f"<strong>Nome: </strong>{contexto['pessoa'].nome}",stylePessoa),Paragraph(f"<strong>Matrícula: </strong>{contexto['pessoa'].id}", stylePessoa),
        Paragraph(f"<strong>Cargo: </strong>{contexto['des_cargo']}", stylePessoa), Paragraph(f"<strong>Disciplina: </strong>{contexto['disciplina']}", stylePessoa)],
        [Paragraph(f"<strong>CPF: </strong>{contexto['pessoa'].cpf}", stylePessoa),Paragraph(f"<strong>Data de Admissão: </strong>{contexto['pessoa'].admissao.strftime('%d/%m/%Y')}", stylePessoa),
        Paragraph(f"<strong>Data de Saída: </strong>{saida}", stylePessoa),
        Paragraph(f"<strong>Efetivo: </strong>{contexto['pessoa'].efetivo}", stylePessoa)]
    ]

    tb_pessoa = Table(data_pessoa,style=([('GRID',(0,0),(-1,-1), 0.5, colors.white),
                            ('LEFTPADDING',(0,0),(-1,-1),2),
                            ('TOPPADDING',(0,0),(-1,-1),2),
                            ('BOTTOMPADDING',(0,0),(-1,-1),2),
                            ('RIGHTPADDING',(0,0),(-1,-1),0),
                            ('ALIGN',(0,0),(-1,-1),'CENTER'),
                            ]), hAlign='CENTER')

    #Send the data and build the file
    elementos.append(tb_pessoa)
    elementos.append(t_frequencia)

    elementos.append(Paragraph(f"", styleB))
    
    elementos.append(Paragraph('____________________________', styleAssTrac))
    elementos.append(Paragraph('', styleAss))
    elementos.append(Paragraph('', styleAss))
    elementos.append(Paragraph('', styleAss))
    
    elementos.append(t_tipos)
    doc.build(elementos)

    nome = contexto["pessoa"].nome.replace(' ', '_')
    data_hora = datetime.now().strftime('_%d_%m_%Y_%H_%M_%S')
    nome_arquivo = f"{nome}{data_hora}.pdf"

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename={nome_arquivo}.pdf'
    response.write(buffer.getvalue())
    buffer.close()

    return response

def pdf_v_original(request, pessoa_id, ano):
    from io import BytesIO

    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.platypus import (Paragraph, SimpleDocTemplate, Table,
                                    TableStyle)
    contexto = buscar_informacoes_ficha_v2(pessoa_id,ano)
   
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, 
                            pagesize=landscape(A4), 
                            rightMargin=30, 
                            leftMargin=30, 
                            topMargin=30,
                            bottomMargin=18)
   
    elements = []

    # cria informações para a primeira linha da tabela
    mes_dias = ["Mês/Dia"]
    for i in range(1,32):
        mes_dias.append(i)
    # mes_dias.append('Tempos')

    # insere a chave dentro da lista dos meses na posição 0. Ex ['janeiro','C','C'...]
    for k,v in contexto['meses'].items():
        v.insert(0,k)

    print("contexto[meses]", contexto)

    # insere no dicionario faltas na posição 0 a sigla da falta Ex 'contexto['FJ']'=['FJ','FALTA JUSTIFICADA',10]
    for k,v in contexto['tp_faltas'].items():
        v.insert(0,k)

    # cria lista com os valores não a chave
    data_tp_falta = [tp for tp in contexto['tp_faltas'].values()]
    
    # cria lista com os valores dos meses 
    data_frequencia = [m for m in contexto['meses'].values()]

    # dentro dessa lista insere a lista mes_dias
    data_frequencia.insert(0, mes_dias)

    faltas_mes_a_mes = contexto['falta_por_mes']
    linha = 0
    eventos_por_mes = []
    intermediaria = []
    
    for k in faltas_mes_a_mes:
        linha +=1
        if k in ['janeiro','marco','maio','julho','agosto','outubro','dezembro']:
            eventos_por_mes.append(list(faltas_mes_a_mes[k].values()))
        elif k in ['abril','junho','setembro','novembro']:
            intermediaria = list(faltas_mes_a_mes[k].values())
            eventos_por_mes.append(intermediaria)
        else:
            intermediaria = list(faltas_mes_a_mes[k].values())
            eventos_por_mes.append(intermediaria)

    # pega chaves de um mes qualquer que será a linha de eventos
    eventos_por_mes.insert(0,list(contexto['falta_por_mes']['janeiro'].keys()))
    
    # extend a tabela frequencia com informação dos eventos
    for i in range(0,len(data_frequencia)):
        data_frequencia[i].extend(eventos_por_mes[i])
    
    linha = []
    linha2 = []
    brancos = 0
    brancos = len(contexto['tp_faltas'])
    brancos += 33
    for i in range(brancos):
        linha.append(' ')
    data_frequencia.insert(1,linha)

    for i in range(brancos):
        linha2.append(' ')
    data_frequencia.insert(0,linha2)

    data_frequencia[0].extend(['Tempos'])
    data_frequencia[1].extend(['Função','Cargo','Unidade'])
    data_frequencia[2].extend([contexto['funcao_a'],contexto['cargo_a'],contexto['ue_a']])
    
    funcao_anual = []
    cargo_anual = []
    ue_anual = []
    for v in contexto['cargo'].values():
        cargo_anual.append(v)
    for v in contexto['funcao'].values():
        funcao_anual.append(v)
    for v in contexto['ue'].values():
        ue_anual.append(v)

    # data_frequencia.extend(cargo)
    print(cargo_anual,funcao_anual,ue_anual)
    inicio_linha = 3
    for i in range(12):
        data_frequencia[inicio_linha].extend([funcao_anual[i],cargo_anual[i],ue_anual[i]])
        inicio_linha += 1
    # print("Cargo",contexto['cargo'],"Funcao",contexto['funcao'],'UE',contexto['ue'])
   
    # data_frequencia[5].extend(['Atribuição'])
    # data_frequencia[6].extend([contexto['cargo_at'], contexto['funcao_at'], contexto['ue_at']])
    # data_frequencia[7].extend(['Anterior'])
    # data_frequencia[8].extend([contexto['cargo_a'], contexto['funcao_a'], contexto['ue_a']])
    # data_frequencia[9].extend(['Atual'])
    # data_frequencia[10].extend([contexto['cargo'], contexto['funcao'], contexto['ue']])

   
    tamanho_fonte = 12
    qtd_eventos = len(contexto['tp_faltas'])
    if  qtd_eventos > 3 :
        if qtd_eventos > 6 and qtd_eventos <= 9:
            tamanho_fonte = tamanho_fonte / qtd_eventos  * 5
        else:
            tamanho_fonte = tamanho_fonte / qtd_eventos  * 3.3

   
    print(tamanho_fonte)

    # cria estilo 
    style_table_corpo = TableStyle([('GRID',(0,0),(-1,-1), 0.5, colors.black),
                            ('LEFTPADDING',(0,0),(-1,-1),2),
                            ('TOPPADDING',(0,0),(-1,-1),2),
                            ('BOTTOMPADDING',(0,0),(-1,-1),2),
                            ('RIGHTPADDING',(0,0),(-1,-1),2),
                            ('ALIGN',(0,0),(-1,-1),'CENTER'),
                            ('FONTSIZE',(0,0), (-1,-1),tamanho_fonte), 
                            ('SPAN',(-3,0),(-1,0)),
                            ('SPAN',(1,2),(31,2))
                            # ('SPAN',(-3,-13),(-1,-12)),
                            # ('SPAN',(-3,-8),(-1,-8)),
                            # ('SPAN',(-3,-6),(-1,-6)),
                            # ('SPAN',(-3,-4),(-1,-4)),
                            # ('BOX',(-3,-13),(-1,-1),2,colors.black),
                            # ('BOX',(32,0),(-1,-1),2,colors.black),
                            # ('BACKGROUND',(32,0),(-4,-1),colors.antiquewhite),
                            # ('BOX',(0,0),(32,13),2,colors.black)             
                            ], spaceBefore=20)

    # cria tabela com as informações de data_faltas
    t_frequencia = Table(data_frequencia, hAlign='CENTER',)

    
    # aplica estilo diferente conforme a condição, ou seja, as faltas ficam com cor de background
    for row, values in enumerate(data_frequencia):
       for column, value in enumerate(values):
        #    print(column, value)
           if value in contexto['tp_faltas']:
               style_table_corpo.add('BACKGROUND',(column,row),(column,row),colors.lightblue)

    t_frequencia.setStyle(style_table_corpo)

    t_tipos = Table(data_tp_falta, style=[('GRID',(0,0),(-1,-1), 0.5, colors.black),
                            ('ALIGN',(0,0),(-1,-1),'CENTER'),
                            ('FONTSIZE',(0,0), (-1,-1),7.5),
                            ('LEFTPADDING',(0,0),(-1,-1),1),
                            ('TOPPADDING',(0,0),(-1,-1),1),
                            ('BOTTOMPADDING',(0,0),(-1,-1),1),
                            ('RIGHTPADDING',(0,0),(-1,-1),1),
                            ], hAlign='LEFT')

    styles = getSampleStyleSheet()
    
    styleH = ParagraphStyle('Cabeçalho',
                            fontSize=20,
                            parent=styles['Heading1'],
                            alignment=1,
                            spaceAfter=14)
    
    styleB = ParagraphStyle('Corpo',
                        spaceAfter=14
                    ) 
    styleAss = ParagraphStyle('Assinatura',
                        alignment=1,
            
                    ) 

    styleAssTrac =  ParagraphStyle('AssinaturaTrac',
                        alignment=1,
                        spaceBefore=20
            
                    ) 

    stylePessoa = ParagraphStyle('Pessoa',
                        # alignment=0,
                        spaceAfter=4
                        
                    ) 
   
    # elements.append(Paragraph('<para><img src="https://www.orlandia.sp.gov.br/novo/wp-content/uploads/2017/01/brasaoorlandia.png" width="40" height="40"/> </para>'))
    elements.append(Paragraph(f"<strong>Ficha Frequência - Ano</strong>:{contexto['ano']}", styleH))
    # elements.append(Paragraph(f"<strong>Nome</strong>: {contexto['pessoa'].nome}  RM: {contexto['pessoa'].id}", styleB))
    
  
    
    saida = '' if contexto['pessoa'].saida == None else  contexto['pessoa'].saida.strftime('%d/%m/%Y')


    data_pessoa = [
        [Paragraph(f"<strong>Nome: </strong>{contexto['pessoa'].nome}",stylePessoa),Paragraph(f"<strong>Matrícula: </strong>{contexto['pessoa'].id}", stylePessoa),
        Paragraph(f"<strong>Cargo: </strong>{contexto['des_cargo']}", stylePessoa), Paragraph(f"<strong>Disciplina: </strong>{contexto['disciplina']}", stylePessoa)],
        [Paragraph(f"<strong>CPF: </strong>{contexto['pessoa'].cpf}", stylePessoa),Paragraph(f"<strong>Data de Admissão: </strong>{contexto['pessoa'].admissao.strftime('%d/%m/%Y')}", stylePessoa),
        Paragraph(f"<strong>Data de Saída: </strong>{saida}", stylePessoa),
        Paragraph(f"<strong>Efetivo: </strong>{contexto['pessoa'].efetivo}", stylePessoa)]
    ]

    tb_pessoa = Table(data_pessoa,style=([('GRID',(0,0),(-1,-1), 0.5, colors.white),
                            ('LEFTPADDING',(0,0),(-1,-1),2),
                            ('TOPPADDING',(0,0),(-1,-1),2),
                            ('BOTTOMPADDING',(0,0),(-1,-1),2),
                            ('RIGHTPADDING',(0,0),(-1,-1),0),
                            ('ALIGN',(0,0),(-1,-1),'CENTER'),
                            ]), hAlign='CENTER')

    #Send the data and build the file
    elements.append(tb_pessoa)
    elements.append(t_frequencia)

    elements.append(Paragraph(f"", styleB))
    
    elements.append(Paragraph('____________________________', styleAssTrac))
    elements.append(Paragraph('', styleAss))
    elements.append(Paragraph('',styleAss))
    elements.append(Paragraph('',styleAss))
    
    elements.append(t_tipos)
    doc.build(elements)
    nome_arquivo = str(contexto["pessoa"].nome).replace(' ','_') + datetime.strftime(datetime.now(),'_%d/%m/%Y_%H_%M_%S')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={nome_arquivo}.pdf'
    response.write(buffer.getvalue())
    buffer.close()

    return response

# implementação requerimento abonada 11/12/2025 
import io
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (Frame, PageTemplate, Paragraph,
                                SimpleDocTemplate, Spacer)

# Importações de classes/funções fictícias necessárias no contexto do seu projeto Django:
# from .models import Servidor # Assumindo um modelo de Servidor
# from .utils import retornarNomeMes # Função para formatar o nome do mês em português


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

# Função principal adaptada
def emitir_abonada(request, lancamento_id):
    """
    Gera um PDF de Requerimento de Falta Abonada baseado no template anexo.
    Os dados do servidor e da falta devem ser passados via POST.
    """
    pessoas_faltas = Faltas_Pessoas.objects.get(id=lancamento_id)
    pessoa = pessoas_faltas.pessoa
    
    
    # -----------------------------------------------------
    # DADOS OBTIDOS DA REQUISIÇÃO (EXEMPLOS)
    # -----------------------------------------------------
    # Você precisará adaptar a forma de obtenção destes dados
    servidor_nome = request.POST.get("nome_servidor", pessoa.nome)
    servidor_matricula = request.POST.get("matricula_servidor", pessoa.id)
    setor_lotacao = request.POST.get("setor_lotacao", "no setor da Educação, na EMEB Profª. Victória Olivito Nonino") # Exemplo baseado no anexo [cite: 4]
    data_falta = request.POST.get("data_falta", pessoas_faltas.data) # Data da falta abonada (ex: dd/mm/aaaa)
    data_formatada = f"{data_falta.day:02d}/{data_falta.month:02d}/{data_falta.year}"
    
    data_pedido = calcular_data_pedido(data_falta)

    buffer = io.BytesIO()

    # -----------------------------------------------------
    # ESTILOS
    # -----------------------------------------------------
    # Mantendo apenas os estilos necessários e adaptando o alinhamento
    corpo = ParagraphStyle(
        name="Corpo",
        fontSize=14,
        alignment=4,  # Justificado
        firstLineIndent=1.5 * cm, # Remove o recuo da primeira linha
        spaceBefore=15,
        leading=24,
    )
    
    titulo = ParagraphStyle(
        name="Titulo",
        fontSize=18,
        alignment=1,  # Centralizado
        spaceAfter=40,
        
    )

    style_direita = ParagraphStyle(
        name="Direita",
        fontSize=14,
        alignment=2,  # Direita
        spaceBefore=1,
        spaceAfter=1,
    )

    style_assinatura = ParagraphStyle(
        name="Assinatura",
        fontSize=12,
        alignment=1, # Centralizado
        spaceBefore=10,
        spaceAfter=5,
    )
    
    style_autorizacao = ParagraphStyle(
        name="Autorizacao",
        fontSize=12,
        alignment=0, # Esquerda
        spaceBefore=15,
        spaceAfter=25,
        leftIndent=1.5*cm,
    )

    # -----------------------------------------------------
    # DOCUMENTO BASE
    # -----------------------------------------------------
    pdf = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin= 6 * cm,
        bottomMargin=2 * cm,
    )
    
    frame = Frame(
        pdf.leftMargin,
        pdf.bottomMargin,
        pdf.width,
        pdf.height,
        id="normal",
    )

    # Não incluiremos o cabeçalho de imagem para simplificar, 
    # -----------------------------------------------------

    # -----------------------------------------------------
    # CABEÇALHO COM IMAGEM (FORMA CORRETA)
    # -----------------------------------------------------
    header_img = Image(
        "appAluno/static/appAluno/jpeg/cabecalho_600dpi.png",
        width=500,
        height=120,
    )

    def header(canvas, doc, img):
        canvas.saveState()
        img.drawOn(canvas, doc.leftMargin, A4[1] - 150)
        canvas.restoreState()

    template = PageTemplate(
        id="template",
        frames=frame,
        onPage=partial(header, img=header_img),
    )

    pdf.addPageTemplates([template])

    # -----------------------------------------------------
    # CONTEÚDO DO PDF
    # -----------------------------------------------------
    story = []

    # Título
    story.append(Paragraph("<b><u>REQUERIMENTO DE FALTA ABONADA</u></b>", titulo))

    # Corpo do Requerimento
    texto_requerimento = f"""
    Eu, <b>{servidor_nome}</b>, matrícula nº.: <b>{servidor_matricula}</b>, lotado(a) 
     {setor_lotacao}, venho através deste, nos devidos termos da Lei nº. 
    3.841 de 06 de Dezembro de 2011, solicitar autorização para gozo de 
    uma falta abonada, na data de <b>{data_formatada}</b>.
    """
    story.append(Paragraph(texto_requerimento, corpo))
    
    story.append(Spacer(1, 10))

    # [cite_start]Termos em que, pede deferimento [cite: 7]
    story.append(Paragraph("Termos em que, pede deferimento.", corpo))

    story.append(Spacer(1, 40))

    # [cite_start]Data do Pedido (Orlândia, [cite: 8])
    data_emissao = Paragraph(
        f"Orlândia, {data_pedido.day} de {retornarNomeMes(data_pedido.month)} de {data_pedido.year}.",
        style_direita,
    )
    story.append(data_emissao)

    story.append(Spacer(1, 50))
    
    # [cite_start]Assinatura do Funcionário 
    story.append(
        Paragraph(
            f"""____________________________________________<br/>
            (ASSINATURA DO FUNCIONÁRIO/SERVIDOR)""",
            style_assinatura,
        )
    )
    
    story.append(Spacer(1, 50))

    # [cite_start]Autorização/Deferimento [cite: 11]
    # Usando uma tabela ou combinação de parágrafos para simular os campos de deferimento/assinatura
    # Aqui optamos por parágrafos para manter a simplicidade com reportlab's flowables
    
    # Campo Deferido/Indeferido (Opcional)
    story.append(
        Paragraph(
            "Deferido (  ) &nbsp; &nbsp; &nbsp; &nbsp; Indeferido (  )",
            style_autorizacao,
        )
    )

    # Assinatura do Superior Imediato
    story.append(
        Paragraph(
            """__________________________________<br/>
            Superior Imediato/Diretor(a)""",
            style_autorizacao,
        )
    )
    
    # [cite_start]Data da Autorização [cite: 12]
    story.append(
        Paragraph(
            "<br/><br/><br/><br/>Orlândia, ____ de ________________ de ______.",
            style_autorizacao,
        )
    )

    # -----------------------------------------------------
    # GERAR PDF
    # -----------------------------------------------------
    pdf.build(story)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="Requerimento_Abonada_{servidor_matricula}.pdf"'
    response.write(buffer.getvalue())
    buffer.close()
    return response

# Exemplo de como você precisaria configurar a requisição (se fosse um formulário):
# Para testar, você precisará garantir que o objeto 'request' no seu ambiente Django
# contenha os dados POST esperados.


def atualizar_pontuacoes(request, pontuacao_id, pessoa_id):

    pontuacao = Pontuacoes.objects.get(pk=pontuacao_id)
    pontuacoes = Pontuacoes.objects.filter(pessoa=pessoa_id)
    pessoa = Pessoas.objects.get(pk=pessoa_id)

    if request.method == 'POST':
        form = formularioPontuacao(request.POST, instance=pontuacao)
        
        if form.is_valid():
           
            form.save()
            
            messages.success(request,"Pontuação Gravada!")
            return redirect('lancarpontuacao',pessoa_id)
        else:
            messages.error(request,"Erro ao  Gravar Pontuação!",'danger')
            

    else:
        form = formularioPontuacao(instance=pontuacao,initial={'pessoa':pessoa})
    
    return render(request,'template/lancar_pontuacao.html',{'form':form,'pessoa':pessoa,'pontuacoes':pontuacoes})

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

def criar_salvar_pontuacao(ano, funcao, cargo, ue, pessoa):
    pontuacao = Pontuacoes(ano=ano,funcao=funcao,cargo=cargo,ue=ue,pessoa=pessoa)
    pontuacao.save()


def encerrar_ano_v2(request, pessoa_id, ano):
    
    pontuacao_ano_corrente = Pontuacoes.objects.filter(pessoa=pessoa_id).filter(ano=ano)
    pontuacao_ano_anterior= Pontuacoes.objects.filter(pessoa=pessoa_id).filter(ano=ano-1)

    pessoa = Pessoas.objects.get(pk=pessoa_id)
    dicionario =   gerar_pontuacao_anual_v2(ano,pessoa)
   
    funcao = dicionario[0]['dezembro']
    cargo = dicionario[1]['dezembro']
    ue = dicionario[2]['dezembro']

    # anos, pessoa = listar_anos(pessoa.id)
    anos_status, anos = consultar_anos_status(pessoa.id)
    min_ano = min(anos)
     
   
    if request.method == 'GET':

        if  not pontuacao_ano_corrente.exists() and  min_ano == ano and pessoa.efetivo == True:
            criar_salvar_pontuacao(ano, funcao, cargo, ue, pessoa)
            messages.success(request,f"Ano {ano} fechado com sucesso!")

        
        elif pontuacao_ano_anterior.exists():
            criar_salvar_pontuacao(ano, funcao, cargo, ue, pessoa)
            messages.success(request,f"Ano {ano} fechado com sucesso!")

        elif not pontuacao_ano_corrente.exists() and  not pessoa.efetivo :
            criar_salvar_pontuacao(ano, funcao, cargo, ue, pessoa)
            messages.success(request,f"Ano {ano} fechado com sucesso!")


        else:
            messages.info(request,f"Ano anterior {ano - 1} aberto!")
        return redirect('listarficha',pessoa_id)
          

    return render(request,'template/listar_ficha.html',{'anos':anos_status, 'pessoa':pessoa})

def deletar_pontuacao_ano(pessoa, ano):
    if not ano:
        return
    Pontuacoes.objects.filter(pessoa=pessoa).filter(ano__in=ano).delete()
   
def abrir_ano(request, pessoa_id, ano):

    pessoa = Pessoas.objects.get(pk=pessoa_id)
    # anos, pessoa = listar_anos(pessoa_id)
    anos_status, anos = consultar_anos_status(pessoa.id)
    pontuacao_existe= Pontuacoes.objects.filter(pessoa=pessoa_id).filter(ano=ano+1).exists()
    min_ano, max_ano = min(anos), max(anos)
    abrir_todos = (ano == min_ano and pessoa.efetivo)

    if request.method == 'GET':
        
        if abrir_todos:
            
            deletar_pontuacao_ano(pessoa, anos)
        
            messages.success(request,f"Aberto do ano {min_ano} ao {max_ano}")

        else:

            if pontuacao_existe and pessoa.efetivo:
                messages.info(request,f"Não pode abrir {ano} existe ano posterior Fechado!")

            else:
                deletar_pontuacao_ano(pessoa, [ano])  
                messages.success(request,f"Ano {ano} Aberto!")
          
        return redirect('listarficha',pessoa_id)     
   
    return render(request,'template/listar_ficha.html',{'anos':anos_status, 'pessoa':pessoa})

def excluir_pontuacoes(request, pessoa_id, pontuacao_id):
    pontuacao = Pontuacoes.objects.get(pk=pontuacao_id)
    pontuacoes = Pontuacoes.objects.filter(pessoa=pessoa_id).order_by('ano')
    pessoa = Pessoas.objects.get(pk=pessoa_id)

    if request.method == 'GET':
        pontuacao.delete()    
        messages.success(request,"Pontuação Apagada!")
        return redirect('lancarpontuacao',pessoa_id)     
    else:
        form = formularioPontuacao(initial={'pessoa':pessoa})
    
    return render(request,'template/lancar_pontuacao.html',{'form':form,'pessoa':pessoa,'pontuacoes':pontuacoes})

def lancar_pontuacoes(request, pessoa_id):

    pessoa = Pessoas.objects.get(pk=pessoa_id)
    pontuacoes = Pontuacoes.objects.filter(pessoa=pessoa_id).order_by('ano')
    ativo = verificar_ano_saida(pessoa_id)
    if request.method == 'POST':
        form = formularioPontuacao(request.POST)
        ano = form['ano'].value()
        if pessoa.admissao.year <= int(ano) and ativo :
            if form.is_valid():
            
                form.save()
                messages.success(request,"Pontuação Gravada!")
                return redirect('lancarpontuacao',pessoa_id)
            else:
                messages.error(request,"Erro ao  Gravar Pontuação!",'danger')
        else:
            if pessoa.saida == None:
                messages.error(request,f"Erro ao  Gravar Pontuação! Ano Admissao: {pessoa.admissao.year}",'danger')

            else:
                messages.error(request,f"Erro ao  Gravar Pontuação! Ano Admissao: {pessoa.admissao.year} Ano Saída: {pessoa.saida.year}",'danger')


    else:
        form = formularioPontuacao(initial={'pessoa':pessoa})
        
    
    return render(request,'template/lancar_pontuacao.html',{'form':form,'pessoa':pessoa,'pontuacoes':pontuacoes})

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

def coletivo(request):

    return render(request,'template/coletivo.html')


# Verificar 26/12/2022
def lancar_evento_coletivo(request):
    cargos = Cargos.objects.all()
    
    if request.method == 'POST':
        #Captura os valores do formulário
        cargos_selecionados = request.POST.getlist('cargos')
        pessoas = Pessoas.objects.filter(cargo__id__in=cargos_selecionados)
        lancamento_a_criar = []
        conflitos, fechamentos = 0, 0
        

        # instância do formulário para pegar dados
        form = formularioLF(request.POST)
        
        # pegar valores do formulário
        qtd_dias = int(form.data['qtd_dias'])
        data_lancamento = datetime.strptime(form['data'].value(), '%Y-%m-%d').date()
        falta = Faltas.objects.get(pk=form['falta'].value())

        # criar intervalos de lançamentos na memória e dividir por ano (ano é chave)
        dia_mes_ano = gerar_lancamento_em_memoria(data_lancamento,qtd_dias)

        # verifica se os dados preenchidos são válidos
        # verifica se existe faltas naquele intervalo
        for pessoa in pessoas:
            if data_lancamento <= pessoa.admissao:
                continue

            conflito= lancar_falta(data_lancamento, qtd_dias ,pessoa.id)
            ano_fechado = verificar_status_ano(data_lancamento.year, pessoa.id)
            
            if ano_fechado:
                fechamentos += 1
                continue 

            if not conflito:
                conflitos += 1
                continue

            # navega entre os valores de cada chave que é ano
            for datas in dia_mes_ano.values():
                qtd_dias = len(datas) # quantos dias existem dentro da chave ano
                data_lancamento = datas[0] # pega o primeiro dia do lançamento e depois o primeiro dia do ano seguinte
                # cria objeto com os novos dados
                novoLancamento= Faltas_Pessoas(pessoa=pessoa,data=data_lancamento,qtd_dias=qtd_dias,falta=falta)
                # adiciona os objetos a uma lista
                lancamento_a_criar.append(novoLancamento)
                
               
        # Salva objetos de uma só vez no banco
        Faltas_Pessoas.objects.bulk_create(lancamento_a_criar)

        messages.success(request, f"Lançamentos efetuados com sucesso: {len(lancamento_a_criar)}","success")
        messages.error(request, f"Lançamentos com conflitos de datas: {conflitos}","danger")
        messages.warning(request, f"Lançamentos com o ano fechado: {fechamentos}","warning")
              
    else:          
        form = formularioLF()

    return render(request,'template/lancar_evento_coletivo.html', {'form':form, 'cargos': cargos})


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)