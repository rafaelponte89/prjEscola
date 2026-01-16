from functools import partial
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import PageTemplate
from reportlab.platypus.frames import Frame
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle

from aluno.models.matricula import Matricula
from aluno.models.telefone import Telefone
from aluno.models.classe import Classe
from aluno.models.aluno import Aluno
from utilitarios.utilitarios import retornarNomeMes
from datetime import datetime
from aluno.services.aluno import gerarIntervalo
from .header import header_com_imagem

IMG_CABECALHO = "aluno/static/aluno/jpeg/cabecalho_600dpi.png"

def criar_base_pdf(buffer, tamanho_pagina=A4):
    pdf = SimpleDocTemplate(
        buffer,
        pagesize=tamanho_pagina,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=0.5 * cm,
    )

    ALTURA_HEADER = 2.0 * cm  # ajuste conforme sua imagem

    frame = Frame(
        pdf.leftMargin,
        pdf.bottomMargin,
        pdf.width,
        pdf.height - ALTURA_HEADER,
        id="normal",
        topPadding=12
    )

    return pdf, frame


    
def emitir_declaracao_matricula(aluno, nome_operador, cargo_operador, rg_operador, buffer):
    
  
    matricula = (
       Matricula.objects.filter(aluno=aluno).order_by('-ano').first()
    )

    # -----------------------------------------------------
    # ESTILOS
    # -----------------------------------------------------
    style = ParagraphStyle(
        name="Normal",
        fontSize=10,
        alignment=1,
    )

    corpo = ParagraphStyle(
        name="Corpo",
        fontSize=14,
        alignment=4,
        firstLineIndent=40,
        spaceBefore=15,
        leading=24,
    )

    titulo = ParagraphStyle(
        name="Titulo",
        fontSize=18,
        alignment=1,
        spaceAfter=40,
    )

    style_data = ParagraphStyle(
        name="Data",
        fontSize=14,
        alignment=2,
        spaceAfter=40,
    )

    pdf, frame = criar_base_pdf(buffer)
    
    # -----------------------------------------------------
    # CABEÇALHO COM IMAGEM (FORMA CORRETA)
    # -----------------------------------------------------
    template = PageTemplate(
    id="template",
    frames=frame,
    onPage=partial(
        header_com_imagem,
        caminho_imagem=IMG_CABECALHO,
        largura=500,
        altura=120,
    ),
    )

    pdf.addPageTemplates([template])

    # -----------------------------------------------------
    # CONTEÚDO DO PDF
    # -----------------------------------------------------
    story = []

    # Quebras iniciais para descer o conteúdo abaixo do cabeçalho
    story.append(Paragraph("<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>", style))

    data = datetime.now()
    data_emissao = Paragraph(
        f"Orlândia, {data.day} de {retornarNomeMes(data.month)} de {data.year}.",
        style_data,
    )
    story.append(data_emissao)

    print("Matricula",matricula)
    if matricula is not None:
        descritivo_situacao = matricula.retornarDescricaoSituacao()
      

        # Título
        if matricula.situacao == "C":
            story.append(Paragraph("<b><u>Declaração de Matrícula</u></b>", titulo))
            story.append(
                Paragraph(
                    f"""Declaro, para os devidos fins de direito, que o(a) aluno(a) 
                    <b>{aluno.nome}</b>, portador(a) do RA Escolar: 
                    <b>{aluno.ra} - {aluno.d_ra} SP</b>, está <b>{descritivo_situacao}</b> 
                    o <b>{matricula.classe}</b> do Ensino Fundamental de 9 anos nesta 
                    unidade no ano letivo de <b>{matricula.ano}</b>.""",
                    corpo,
                )
            )

        elif matricula.situacao == "BXTR":
            dt_n = datetime.strftime(aluno.data_nascimento,"%d/%m/%Y") if aluno.data_nascimento else ''
            story.append(Paragraph("<b><u>Declaração de Transferência</u></b>", titulo))
            story.append(
                Paragraph(
                    f"""Declaro para os devidos fins de direito, que o(a) aluno(a) 
                    <b>{aluno.nome}</b>, nascido(a) em <b>{dt_n}</b>,
                    portador(a) do RA Escolar <b>{aluno.ra} - {aluno.d_ra}</b> do 
                    <b>{matricula.classe}</b> do Ensino Fundamental de 9 anos nesta unidade escolar,
                    solicitou na presente data <b>transferência</b>, estando apto(a) ao prosseguimento 
                    de estudos no <b>{matricula.classe.serie}º ano</b> do Ensino Fundamental de 9 anos.""",
                    corpo,
                )
            )

        story.append(
            Paragraph("Por ser expressão da verdade, firmo a presente declaração.", corpo)
        )

    else:
        story.append(Paragraph("<b>Sem informações a exibir.</b>", titulo))

    # Espaço antes da assinatura
    story.append(Paragraph("<br/><br/><br/><br/><br/>", style))

    # Assinatura
    story.append(
        Paragraph(
            f"""________________________________<br/>
            {nome_operador}<br/>{cargo_operador}<br/>RG: {rg_operador}""",
            style,
        )
    )
    pdf.build(story)
    
    return buffer

def emitir_lista_rm(rmi, rmf, buffer):
    
    maior = ''
    if rmi > rmf:
        maior = rmi
        rmi = rmf
        rmf = maior
        
    
    alunos = gerarIntervalo(rmi, rmf)
    elements = []
   
    doc = SimpleDocTemplate(buffer, rightMargin=30, leftMargin=50, topMargin=30, bottomMargin=20)
    
    primeira_linha = ['RM', 'Nome']
    data_alunos = []
    data_alunos.append(primeira_linha)
    stylesheet = getSampleStyleSheet()
    normalStyle = stylesheet['BodyText']
    
    for a in alunos:
        if a['status'] == Aluno.STATUS_CANCELADO:
            data_alunos.append([Paragraph(f'<para align=center size=12><strike>{a["rm"]}</strike></para>',normalStyle), Paragraph(f'<para size=12><strike>{a["nome"]}</strike></para>')])
        else:
            data_alunos.append([Paragraph(f'<para align=center size=12>{a["rm"]}</para>',normalStyle), Paragraph(f'<para size=12>{a["nome"]}</para>')])
        
    style_table = TableStyle(([('GRID',(0,0),(-1,-1), 0.5, colors.white),
                            ('LEFTPADDING',(0,0),(-1,-1),6),
                            ('TOPPADDING',(0,0),(-1,-1),4),
                            ('BOTTOMPADDING',(0,0),(-1,-1),3),
                            ('RIGHTPADDING',(0,0),(-1,-1),6),
                            ('ALIGN',(0,0),(-1,-1),'LEFT'),
                             ('ALIGN',(0,0),(0,-1),'CENTER'),
                            ('BACKGROUND',(0,0),(1,0), colors.lavender),
                            ('LINEBELOW',(0,0),(-1,-1),1, colors.black),
                            ('FONTSIZE',(0,0), (-1,-1), 13)
                            ]))
    
    t_aluno = Table(data_alunos, style=style_table, hAlign='LEFT', repeatRows=1, colWidths=[60, 450])
    
    elements.append(t_aluno)
    
    doc.build(elements)
    return buffer

def emitir_lista_telefonica(classe, buffer):
    matriculas = Matricula.objects.filter(classe=classe).order_by('numero')
    
    telefones = ''
    elements = []
    
    doc = SimpleDocTemplate(buffer, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=20, pagesize=(A4[1], A4[0]))
    
    titulo = "Lista Telefônica " + str(classe)
    
    primeira_linha = ['Nº','Nome', 'Telefones']
    data_alunos = []
    data_alunos.append([titulo])
    data_alunos.append(primeira_linha)
    
    for m in matriculas:
        aluno = Aluno.objects.get(pk=m.aluno.rm)
        tel_aluno = Telefone.objects.filter(aluno=aluno)[:6]
        for t in tel_aluno:
            telefones = telefones + str(t) + ' '
        data_alunos.append([m.numero, m.aluno.nome, telefones])
        telefones = ''       
                 
    style_table = TableStyle(([('GRID',(0,1),(-1,-1), 0.5, colors.gray),
                               ('SPAN', (0,0), (2,0)),
                            ('LEFTPADDING',(0,0),(-1,-1),6),
                            ('TOPPADDING',(0,0),(-1,-1),4),
                            ('BOTTOMPADDING',(0,0),(-1,-1),3),
                            ('RIGHTPADDING',(0,0),(-1,-1),6),
                            ('ALIGN',(0,0),(-1,-1),'LEFT'),
                             ('ALIGN',(0,0),(0,-1),'CENTER'),
                            ('BACKGROUND',(0,1),(2,1), colors.lavender),
                            ('FONTSIZE',(0,0), (-1,-1), 13),
                            ('BOTTOMPADDING',(0,0),(0,0),20),
                            ('FONTSIZE',(0,0),(0,0),18),
                            ]))
    
    t_aluno = Table(data_alunos, hAlign='CENTER', 
                    repeatRows=1, style=style_table)
    
    elements.append(t_aluno)
    
    doc.build(elements, )
    return buffer


def emitir_lista_personalizada(classe, titulo_lista, 
                               tamanho_fonte, colunas, 
                                tamanho_colunas, orientacao,
                               repeticao, buffer):    
    
    print('Orientação', orientacao)
    matriculas = (classe.matriculas.
                  filter(situacao='C').
                  order_by('aluno__nome').
                  values('aluno__nome'))
    
    largura, altura =  0, 0
    if orientacao == 'r':
        orientacao = (A4[0], A4[1])  # retrato
        largura = 500
        altura = 80
       
    else:
        orientacao = (A4[1], A4[0])  # paisagem 
        largura = 500
        altura = 80

    titulo = str(titulo_lista) + " - " + str(classe)
    print(titulo)
    primeira_linha = ['Nº','Nome']
    primeira_linha.extend(colunas)
    data_alunos = []
    data_alunos.append([titulo])
    data_alunos.append(primeira_linha)

    pdf, frame = criar_base_pdf(buffer, tamanho_pagina = orientacao)
    
    linha = ''
    count = 0

    for m in matriculas:
        for i in range(1, repeticao + 1):
            count += 1
            linha = [count, m['aluno__nome']]
            for col in range(len(colunas)):
                linha.append(' ' * int(tamanho_colunas[col]) )
            
            data_alunos.append(linha)
    colunas_totais = len(colunas) + 1               
    style_table = TableStyle([('GRID',(0,1),(-1,-1), 0.5, colors.gray),
                               ('SPAN', (0,0), (colunas_totais, 0)),
                            ('LEFTPADDING',(0,0),(-1,-1),6),
                            ('TOPPADDING',(0,0),(-1,-1),4),
                            ('BOTTOMPADDING',(0,0),(-1,-1),3),
                            ('RIGHTPADDING',(0,0),(-1,-1),6),
                            ('ALIGN',(0,0),(-1,-1),'LEFT'),
                             ('ALIGN',(0,0),(0,-1),'CENTER'),
                            ('BACKGROUND',(0,1),(colunas_totais,1), colors.lavender),
                            ('FONTSIZE',(0,0), (-1,-1), 13),
                            ('BOTTOMPADDING',(0,0),(0,0),20),
                            ('FONTSIZE',(0,0),(0,0),18),
                            ('FONTSIZE',(0,2),(-1,-1), tamanho_fonte),
                            ])
    
   
    
    t_aluno = Table(data_alunos, style=style_table, hAlign='CENTER', 
                    repeatRows=2)

    template = PageTemplate(
    id="template",
    frames=frame,
    onPage=partial(
        header_com_imagem,
        caminho_imagem=IMG_CABECALHO,
        largura=largura,
        altura=altura,
    ),
    )
    pdf.addPageTemplates([template])

    # conteudo
    pdf.build([t_aluno])
    return buffer