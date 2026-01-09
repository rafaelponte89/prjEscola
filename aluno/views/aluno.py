
from django.http import HttpResponse
from django.shortcuts import render
import io

from aluno.models.classe import Classe
from aluno.models.matricula import Matricula
from aluno.utils.texto import  padronizar_nome

from aluno.forms.aluno import FrmAluno, FrmAlunoUpdate
from aluno.models.aluno import Aluno
from django.shortcuts import get_object_or_404

from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from aluno.forms.telefone import TelefoneFormSet

from django.db import transaction


REF_TAMANHO_NOME = 2
REF_TAMANHO_RA = 7
EMAIL = "victorianonino@educa.orlandia.sp.gov.br"
from aluno.services.aluno import buscar_duplicados, renderizarTabela, pesquisar_alunos_por_nome
from aluno.services.mensagem import criarMensagemJson


def index(request):
    if request.method == "POST":
        # Se o formulário de cadastro de aluno foi enviado
        return salvar_aluno(request)
    # Se for GET, apenas renderiza o formulário
    form = FrmAluno()
    return render(request, "aluno/aluno/index.html", {"form": form})

# Gravar registro do Aluno
def salvar_aluno(request):
    nome = padronizar_nome(request.POST.get("nome"))
    ra = request.POST.get("ra")

    form = FrmAluno({"nome": nome, "ra": ra})

    # Validação RA duplicado
    if Aluno.objects.filter(ra=ra).exists():
        return JsonResponse({
            'success': False,
            'mensagem': criarMensagemJson(f'Já existe RA {ra} cadastrado para outro aluno!','danger')
        })

    if not form.is_valid():
        return JsonResponse({
            'success': False,
            'mensagem': criarMensagemJson(f'Dados Inválidos!','danger')
        })

    if len(nome) <= REF_TAMANHO_NOME:
        return JsonResponse({
            'success': False,
            'mensagem': criarMensagemJson(f'Nome muito Pequeno!','warning')
        })

    if len(ra) <= REF_TAMANHO_RA:
        return JsonResponse({
            'success': False,
            'mensagem': criarMensagemJson(f'RA muito Pequeno!','warning')
        })

    # Salva aluno
    form.save()

    alunos = Aluno.retornarNUltimos()
    nomes_duplicados = buscar_duplicados(alunos)
    html = renderizarTabela(alunos, nomes_duplicados, request)

    return JsonResponse({
        'success': True,
        'mensagem': criarMensagemJson(f'Aluno Registrado com Sucesso!','success'),
        'html': html
    })


@transaction.atomic
def atualizar_aluno(request):
    aluno = get_object_or_404(Aluno, rm=request.POST.get("rm"))

    form = FrmAlunoUpdate(request.POST, instance=aluno)
    formset = TelefoneFormSet(request.POST, instance=aluno)

    if form.is_valid() and formset.is_valid():
        form.save()
        formset.save()

        return JsonResponse({
            'success': True,
            'mensagem': criarMensagemJson(
                'Aluno atualizado com sucesso!!!',
                'success'
            )
        })

    return JsonResponse({
        'success': False,
        'html': render_to_string(
            'aluno/aluno/partials/form_update.html',
            {
                'form': form,
                'formset': formset,
                'aluno': aluno
            },
            request=request
        )
    })
        
def pesquisar_aluno(request):
    nome = padronizar_nome(request.POST.get("nome", ""))
    filtro = request.POST.get("filtro")

    if len(nome) <= REF_TAMANHO_NOME:
        # Últimos 5 registros
        alunos = Aluno.retornarNUltimos().prefetch_related('telefones')
        nomes_duplicados = buscar_duplicados(alunos)
        html = renderizarTabela(alunos, nomes_duplicados, request)
        return JsonResponse({'html': html, 'mensagem': ''})  # sem mensagem

    alunos = pesquisar_alunos_por_nome(nome, filtro).prefetch_related('telefones')
    nomes_duplicados = buscar_duplicados(alunos)
    html = renderizarTabela(alunos, nomes_duplicados, request)

    if not alunos:
       
        return JsonResponse({'html': '', 'mensagem': criarMensagemJson('Aluno não Encontrado!','info')})
    
    return JsonResponse({'html': html, 'mensagem': ''})
        
def cancelarRM(request):
    rm = request.POST.get("rm")
    try:
        aluno = Aluno.objects.get(rm=rm)
    except Aluno.DoesNotExist:
        return JsonResponse({"success": False, "mensagem":criarMensagemJson('Aluno não Encontrado!', 'info')})

    # Defina explicitamente o status de cancelado
    aluno.status = Aluno.STATUS_CANCELADO
    aluno.save()

    return JsonResponse({"success": False, "mensagem":criarMensagemJson(f'Aluno {aluno.nome}, RM {aluno.rm} Cancelado com Sucesso!', 'success')})
 
def recarregarTabela(request):
    alunos = Aluno.retornarNUltimos().prefetch_related('telefones')
    nomes_duplicados = buscar_duplicados(alunos)
    html = renderizarTabela(alunos, nomes_duplicados, request)
  
    return JsonResponse({'html': html, 'mensagem': ''})  # sem mensagem

def buscar_dados_aluno(request):
    aluno = get_object_or_404(Aluno, rm=request.POST.get("rm"))

    form = FrmAlunoUpdate(instance=aluno)
    formset = TelefoneFormSet(instance=aluno)

    return render(
        request,
        "aluno/aluno/partials/form_update.html",
        {
            "form": form,
            "formset": formset,
            "aluno": aluno,
        }
    )



def buscarRMCancelar(request):
    rm = request.POST.get('rm')
    aluno = Aluno.objects.values('rm', 'nome').get(pk=rm)
    return JsonResponse({"rm": aluno['rm'], "nome": aluno['nome']})

   
# em desenvolvimento 10/05/2024
def buscar_historico_matriculas(request):
    rm = request.POST.get('rm')
    aluno = Aluno.objects.get(pk=rm)
    matriculas_aluno = Matricula.objects.filter(aluno=aluno)
    dados_matricula=''
    
    for matricula in matriculas_aluno:
        descritivo_situacao = Matricula.retornarDescricaoSituacao(matricula)
        dados_matricula += f"""
                   <div class="col-12 form-group d-flex align-items-center"> 
                  <input        
                    type="text"     
                    class="form-control m-2" 
                    title="Início: {(matricula.data_matricula).strftime("%d/%m/%Y")} || Fim: { (matricula.data_movimentacao).strftime("%d/%m/%Y") if matricula.data_movimentacao != None else "-" }"
                   
                    aria-describedby="emailHelp" 
                    placeholder="Ano" 
                    value="{matricula.ano}"
                    disabled
                  /> 
                   <input        
                    type="text"     
                    class="form-control m-2" 
                   
                    aria-describedby="emailHelp" 
                    placeholder="Ano" 
                    value=" {descritivo_situacao}"
                    disabled
                  /> 
                      
                      <input        
                    type="text"     
                    class="form-control m-2" 
                    
                    aria-describedby="emailHelp" 
                    placeholder="Ano" 
                    value="{matricula.classe}"
                    disabled
                  /> 
                </div>"""
    
    return HttpResponse(dados_matricula)

      

## Nova Personalizável
def footer(canvas, doc, content):
    canvas.saveState()
    w, h = content.wrap(doc.width, doc.bottomMargin)
    content.drawOn(canvas, doc.leftMargin, h)

    canvas.restoreState()

def header_and_footer(canvas, doc, header_content, footer_content):
    header(canvas, doc, header_content,)
    footer(canvas, doc, footer_content)

def header(canvas, doc, content):
        canvas.saveState()
        w, h = content.wrap(doc.width, doc.topMargin)
        content.drawOn(canvas, doc.leftMargin, doc.height + doc.bottomMargin + doc.topMargin - h)
        canvas.restoreState()
        
def baixar_lista_alunos_personalizavel(request):
    from functools import partial

    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import PageTemplate, SimpleDocTemplate, Table, TableStyle
    from reportlab.platypus.frames import Frame
    from reportlab.platypus.paragraph import Paragraph
    from reportlab.lib import colors

    
    classe = Classe.objects.get(pk=int(request.POST.get("classe")))

    titulo_lista = request.POST.get('titulo')
    tamanho_fonte = float(request.POST.get('tamanho_fonte'))
    colunas_em_branco = (request.POST.get('colunas')).split(',')
   
    tamanho_colunas_em_branco = (request.POST.get('tam_colunas')).split(',')
    
    tipo_pagina = request.POST.get('pagina')
    repeticao = int(request.POST.get('repeticao'))

    if tipo_pagina == 'r':
        tamanho_pagina = (A4[0], A4[1])  # retrato
    else:
        tamanho_pagina = (A4[1], A4[0])  # paisagem

    classe = Classe.objects.get(pk=int(request.POST.get("classe")))
    matriculas = (Matricula.objects.filter(classe=classe).
                  filter(situacao='C').
                  order_by('aluno__nome'))

    
    buffer = io.BytesIO()

    titulo = str(titulo_lista) + " - " + str(classe)
    print(titulo)
    primeira_linha = ['Nº','Nome']
    primeira_linha.extend(colunas_em_branco)
    data_alunos = []
    data_alunos.append([titulo])
    data_alunos.append(primeira_linha)



    style = ParagraphStyle(
        name='Normal',
        fontSize=10,
        alignment=1
    )



    pdf = SimpleDocTemplate(buffer, pagesize=tamanho_pagina, 
        leftMargin = 1.5 * cm, 
        rightMargin = 1.5 * cm,
        topMargin = 1.5 * cm, 
        bottomMargin = 0.5 * cm)

    frame = Frame(pdf.leftMargin, pdf.bottomMargin, pdf.width, pdf.height, id='normal')
    
    if tipo_pagina == 'r':
        espacos = "&nbsp;" *39
        header_content =( Paragraph(f"""
                               <strong><font size="18">EMEB PROFª VICTÓRIA OLIVITO NONINO </font></strong> <br/>
                                 Rua 14, 1303 A - Conjunto Habtacional José Luís Simões - Orlândia - SP - (16)3820-8230  <br/>
                                 <img src="aluno/static/aluno/jpeg/logo_prefeitura.jpg" valign="middle" height="50" width="50" />{espacos}{EMAIL}{espacos}<img src="aluno/static/aluno/jpeg/logo_escola.jpg" valign="middle" height="50" width="50" />""", style=style ) )
      
    
    else:
        espacos = "&nbsp;" * 53
        header_content =( Paragraph(f"""
                               <strong><font size="18">EMEB PROFª VICTÓRIA OLIVITO NONINO </font></strong> <br/>
                                 Rua 14, 1303 A - Conjunto Habtacional José Luís Simões - Orlândia - SP - (16)3820-8230  <br/>
                                 <img src="aluno/static/aluno/jpeg/logo_prefeitura.jpg" valign="middle" height="50" width="50" />{espacos}{EMAIL}{espacos}<img src="aluno/static/aluno/jpeg/logo_escola.jpg" valign="middle" height="50" width="50" />""", style=style ) )
                     
    
    count = 0
    linha = ''
    for m in matriculas:
       
        for i in range(1, repeticao + 1):
            count += 1
            linha = [count, str(m.aluno.nome)]
            for col in range(len(colunas_em_branco)):
                linha.append(' ' * int(tamanho_colunas_em_branco[col]) )
            
            data_alunos.append(linha)
    colunas_totais = len(colunas_em_branco) + 1               
    style_table = TableStyle(([('GRID',(0,1),(-1,-1), 0.5, colors.gray),
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
                            ('FONTSIZE',(0,2),(-1,-1), tamanho_fonte)
                            ]))
    
    t_aluno = Table(data_alunos, style=style_table, hAlign='CENTER', 
                    repeatRows=2)

    template = PageTemplate(id='test', frames=frame, onPage=partial(header, content=header_content))

    pdf.addPageTemplates([template])

    # conteudo
    pdf.build([t_aluno], onLaterPages=partial(header, content=header_content))

    response = HttpResponse(content_type='application/pdf')
    
    response.write(buffer.getvalue())
    buffer.close()
    
    return response



