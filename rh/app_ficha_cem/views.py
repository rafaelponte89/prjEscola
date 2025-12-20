# Create your views here.
from datetime import  datetime, timedelta
from io import BytesIO

from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.defaulttags import register
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (Paragraph, SimpleDocTemplate, Spacer,
                                Table, TableStyle)

from rh.app_pessoa.models import Pessoas
from rh.app_pontuacao.models import Pontuacoes
from rh.app_pontuacao.pontuacoes import criar_salvar_pontuacao, deletar_pontuacao_ano

from .forms import (FaltaPesquisaForm, FaltaPesquisaFormGeral,
                    FiltroRelatorioDescritivoForm, formularioLF)
from .models import Cargos, Faltas, Faltas_Pessoas

# importação de afastamentos
from django.shortcuts import render
from .forms import ImportarAfastamentosForm

from django.db.models import Sum
import tempfile

from .services.calculos import gerar_lancamento_em_memoria, gerar_pontuacao_anual_v2
from .services.consultas import (verificar_status_ano, listar_anos, verificar_data_saida, checar_existencia_pontuacao, 
                                buscar_informacoes_ficha_v2, buscar_informacoes_ficha_v3, 
                                consultar_anos_status)

from .services.importacoes import importar_afastamentos_pdf
from .services.transformacoes import inserir_chave
from .services.faltas import lancar_falta

from .services.relatorios import (requerimento_abonada, gerar_relatorio_faltas_descritivo,
                                    gerar_relatorio_faltas_descritivo_pdf, buscar_faltas_geral)
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
    return render(request,'rh/lancar_falta.html', {'form':form, 'pessoa':pessoa, 'faltas':pessoa_falta})


def excluir_pessoas_faltas(request, pessoa_id, lancamento_id):

    lancamento = Faltas_Pessoas.objects.filter(pk=lancamento_id)
    pessoa = Pessoas.objects.get(pk=pessoa_id)
    pessoa_falta = Faltas_Pessoas.objects.filter(pessoa=pessoa).order_by('data')[:30]

    if request.method == 'GET':
        lancamento.delete()    
        messages.success(request,"Lançamento Apagado!")
        return redirect('lancarfalta',pessoa_id)
    
    
    return render(request,'rh/lancar_falta.html', {'pessoa':pessoa, 'faltas':pessoa_falta})
        

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
  
    return render(request,'app_ficha_cem/listar_ficha_v2.html',{'anos':anos_status, 'pessoa':pessoa})

############################# Filtros #########################

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
        qs = buscar_faltas_geral(
            data_inicio=form.cleaned_data['data_inicio'],
            data_fim=form.cleaned_data['data_fim'],
            faltas_selecionadas=form.cleaned_data['falta'],
            cargos_selecionados=form.cleaned_data['cargo'],
            efetivo=form.cleaned_data['efetivo'],
            ativo=form.cleaned_data['ativo'],
        )

        resultados = qs.order_by('data')

        totais_por_tipo = (
            qs.values('falta__descricao')
            .annotate(total_dias=Sum('qtd_dias'))
            .order_by('falta__descricao')
        )

        total_geral = qs.aggregate(
            soma=Sum('qtd_dias')
        )['soma'] or 0

    return render(request, 'rh/relatorio_geral.html', {
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

    return render(request, 'rh/relatorio.html', {
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
        dados_agrupados, total_funcionarios = gerar_relatorio_faltas_descritivo(data_inicial, data_final, efetivo, publico, 
                                                                                dados_agrupados, total_funcionarios)
    return render(request, 'rh/relatorio_faltas_descritivo.html', {
        'form': form,
        'dados': dados_agrupados,
        'total_funcionarios': total_funcionarios
    })


def relatorio_faltas_descritivo_pdf(request):
    
    data_inicio_str = request.GET.get('data_inicio')
    data_fim_str = request.GET.get('data_fim')
    efetivo = request.GET.get('efetivo')
    publico = request.GET.get('publico')

    buffer = gerar_relatorio_faltas_descritivo_pdf(data_inicio_str, data_fim_str, efetivo, publico)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="relatorio_faltas.pdf"'
    
    return response

###### Fim Filtros ###########

def gerar_ficha(request, pessoa_id, ano):
    
    contexto = buscar_informacoes_ficha_v3(pessoa_id, ano)
    return render(request,'app_ficha_cem/ficha_cem_v2.html', {'contexto':contexto})

def index(request):
    
    return render(request,'rh/index.html')
        
def pdf_v3(request, pessoa_id, ano):
    
    contexto = buscar_informacoes_ficha_v2(pessoa_id, ano)
    print("Inicial", contexto)

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
    print(mes_dias)
    # insere a chave dentro da lista dos meses na posição 0. Ex ['janeiro','C','C'...]
    inserir_chave(contexto, "meses")
    print("Meses==================================================", contexto)
    # insere no dicionario faltas na posição 0 a sigla da falta Ex 'contexto['FJ']'=['FJ','FALTA JUSTIFICADA',10]
    inserir_chave(contexto, "tp_faltas")
    print("Tipo Faltas============================================", contexto)
    
    # cria lista com os valores não a chave
    data_tp_falta = [tp for tp in contexto['tp_faltas'].values()]
    print("Data e Tipo Falta=======================", data_tp_falta)
    
    # cria lista com os valores dos meses 
    data_frequencia = [m for m in contexto['meses'].values()]
    print("Meses Frequencia=======================", data_frequencia)

    # dentro dessa lista insere a lista mes_dias
    data_frequencia.insert(0, mes_dias)

    faltas_mes_a_mes = contexto['falta_por_mes']
    linha = 0
    eventos_por_mes = []
    print("Faltas MEs a Mes=====================================================",faltas_mes_a_mes)
   
    # dicionarios aninhados com os meses dentro dos meses os tipos de eventos e a quantidade 17/04/2025
    for k in faltas_mes_a_mes:
        eventos_por_mes.append(list(faltas_mes_a_mes[k].values()))

    # pega chaves de um mes qualquer que será a linha de eventos
    eventos_por_mes.insert(0,list(contexto['falta_por_mes']['janeiro'].keys()))
    print("eventos_por_mes============", eventos_por_mes)
    
    # extend a tabela frequencia com informação dos eventos
    for i in range(0,len(data_frequencia)):
        data_frequencia[i].extend(eventos_por_mes[i])
    
    print("Data frequencia informaç~eos s============", data_frequencia)

  
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
    tamanho_fonte = 7
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

    print("Tabela Frequencia" , t_frequencia)
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



# implementação requerimento abonada 11/12/2025 
def emitir_abonada(request, lancamento_id):
    """
    Gera um PDF de Requerimento de Falta Abonada baseado no template anexo.
    Os dados do servidor e da falta devem ser passados via POST.
    """
    pessoas_faltas = Faltas_Pessoas.objects.get(id=lancamento_id)
    pessoa = pessoas_faltas.pessoa
    
    servidor_nome = request.POST.get("nome_servidor", pessoa.nome)
    servidor_matricula = request.POST.get("matricula_servidor", pessoa.id)
    setor_lotacao = request.POST.get("setor_lotacao", "no setor da Educação, na EMEB Profª. Victória Olivito Nonino") # Exemplo baseado no anexo [cite: 4]
    data_falta = request.POST.get("data_falta", pessoas_faltas.data) # Data da falta abonada (ex: dd/mm/aaaa)
    data_formatada = f"{data_falta.day:02d}/{data_falta.month:02d}/{data_falta.year}"
    
    buffer = requerimento_abonada(servidor_nome, servidor_matricula, setor_lotacao, data_formatada, data_falta)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="Requerimento_Abonada_{servidor_matricula}.pdf"'
    response.write(buffer.getvalue())
    buffer.close()
    
    return response



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
   
    return render(request,'app_ficha_cem/listar_ficha.html',{'anos':anos_status, 'pessoa':pessoa})






def coletivo(request):

    return render(request,'rh/coletivo.html')

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

    return render(request,'rh/lancar_evento_coletivo.html', {'form':form, 'cargos': cargos})


def importar_afastamentos(request):
    if request.method == "POST":
        form = ImportarAfastamentosForm(request.POST, request.FILES)

        if form.is_valid():
            arquivo = form.cleaned_data["arquivo"]

            # salvar temporariamente
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                for chunk in arquivo.chunks():
                    tmp.write(chunk)
                caminho_pdf = tmp.name

            resultado = importar_afastamentos_pdf(caminho_pdf)

            return render(
                request,
                "rh/importar_resultado.html",
                {"resultado": resultado}
            )
    else:
        form = ImportarAfastamentosForm()

    return render(
        request,
        "rh/importar_afastamentos.html",
        {"form": form}
    )

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)