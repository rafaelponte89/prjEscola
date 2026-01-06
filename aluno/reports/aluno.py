from functools import partial

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import PageTemplate
from reportlab.platypus.frames import Frame
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle

from aluno.models.matricula import Matricula
from aluno.models.aluno import Telefone
from aluno.models.classe import Classe
from aluno.models.aluno import Aluno
from utilitarios.utilitarios import retornarNomeMes
from datetime import datetime
from aluno.services.aluno import gerarIntervalo
from .header import header_com_imagem

EMAIL = 'victorianonino@educa.orlandia.sp.gov.br'

def criar_base_pdf(buffer):
     # -----------------------------------------------------
    # DOCUMENTO BASE
    # -----------------------------------------------------
    pdf = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=0.5 * cm,
    )

    frame = Frame(
        pdf.leftMargin,
        pdf.bottomMargin,
        pdf.width,
        pdf.height,
        id="normal",
    )
    
    return pdf, frame

    
def emitir_declaracao_matricula(aluno, nome_operador, cargo_operador, rg_operador, buffer):
    
    matricula = (
        Matricula.objects.filter(aluno=aluno)
        .order_by("ano")
        .last()
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
        caminho_imagem="aluno/static/aluno/jpeg/cabecalho_600dpi.png",
        largura=500,
        altura=120,
        margem_y=150,
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

    if matricula is not None:
        descritivo_situacao = Matricula.retornarDescricaoSituacao(matricula)
      

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
            dt_n = aluno.data_nascimento if aluno.data_nascimento else ''
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