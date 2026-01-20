
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Frame,
    PageTemplate,
    TableStyle, 
    Table
)
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
import io
from django.http import HttpResponse
from datetime import datetime
from functools import partial
from rh.app_ficha_cem.services.configuracoes import retornarNomeMes
from .calculos import calcular_data_pedido
from rh.app_ficha_cem.models import Faltas_Pessoas
from datetime import datetime

 # -----------------------------------------------------
    # CABEÇALHO COM IMAGEM (FORMA CORRETA)
    # -----------------------------------------------------

HEADER_IMG = Image(
        "aluno/static/aluno/jpeg/cabecalho_600dpi.png",
        width=500,
        height=120,
    )

STR_TO_BOOL = {
        'sim': True,
        'nao': False
}

def gerar_relatorio_faltas_descritivo(data_inicial, data_final, 
                                      efetivo, publico, dados_agrupados,
                                      total_funcionarios):
    
    
    efetivo = STR_TO_BOOL.get(efetivo)
    publico = STR_TO_BOOL.get(publico, False)
   
    registros = (
        Faltas_Pessoas.objects
        .filter(data__range=(data_inicial, data_final))
        .select_related('pessoa', 'falta')
    )
    
    if efetivo is not None:
        registros = registros.filter(pessoa__efetivo=efetivo)

    registros = registros.filter(pessoa__func_publico=publico)

    registros = registros.order_by(
        'pessoa__nome',
        'falta__descricao',
        'data'
    )
        
    dados_agrupados = {}
    
    for registro in registros:
        pessoa = registro.pessoa
        
        dados_agrupados.setdefault(pessoa.id,{
            'matricula': pessoa.id,
            'nome': pessoa.nome,
            'faltas': []
        })
        
        dados_agrupados[pessoa.id]['faltas'].append({
            'data': registro.data,
            'tipo': registro.falta.descricao,
            'qtd_dias': registro.qtd_dias
        })
    total_funcionarios = len(dados_agrupados)
    
    return dados_agrupados, total_funcionarios
       
    
def requerimento_abonada(servidor_nome, servidor_matricula, setor_lotacao, data_formatada, data_falta):
    
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

   

    def header(canvas, doc, img):
        canvas.saveState()
        img.drawOn(canvas, doc.leftMargin, A4[1] - 150)
        canvas.restoreState()

    template = PageTemplate(
        id="template",
        frames=frame,
        onPage=partial(header, img=HEADER_IMG),
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

   
    return buffer

def gerar_relatorio_faltas_descritivo_pdf(data_inicio_str, data_fim_str, efetivo, publico):
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

    buffer = io.BytesIO()

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

    return buffer

def buscar_faltas_geral(
    data_inicio,
    data_fim,
    faltas_selecionadas=None,
    cargos_selecionados=None,
    efetivo=None,
    ativo=None,
):
    qs = (
        Faltas_Pessoas.objects
        .select_related('pessoa', 'falta')
        .filter(data__range=(data_inicio, data_fim))
    )

    if faltas_selecionadas:
        qs = qs.filter(falta__in=faltas_selecionadas)

    if cargos_selecionados:
        qs = qs.filter(pessoa__cargo__in=cargos_selecionados)

    if efetivo in STR_TO_BOOL:
        qs = qs.filter(pessoa__efetivo=STR_TO_BOOL[efetivo])

    if ativo in STR_TO_BOOL:
        qs = qs.filter(pessoa__ativo=STR_TO_BOOL[ativo])

    return qs

def gerar_relatorio_abono(servidor, ano):
    pass
    