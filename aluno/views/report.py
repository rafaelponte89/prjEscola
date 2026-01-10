from aluno.models.aluno import Aluno
from aluno.models.classe import Classe
from django.http import HttpResponse
from aluno.reports.aluno import (emitir_declaracao_matricula, emitir_lista_rm, 
                                 emitir_lista_telefonica, emitir_lista_personalizada)
from io import BytesIO
from datetime import datetime

# Em Desenvolvimento 05/05/2024
def baixar_declaracao_matricula(request):
   
    print("RM", request.POST.get("rm"))
    aluno = Aluno.objects.get(pk=request.POST.get("rm"))
    nome_operador = request.POST.get("nome_op")
    cargo_operador = request.POST.get("cargo_op")
    rg_operador = request.POST.get("rg_op")
    buffer = BytesIO()

    buffer = emitir_declaracao_matricula(aluno, nome_operador, cargo_operador, rg_operador, buffer)
    # -----------------------------------------------------
    # GERAR PDF
    # -----------------------------------------------------

    response = HttpResponse(content_type="application/pdf")
    response.write(buffer.getvalue())
    buffer.close()
    return response


def baixar_pdf(request):

    rmi = int(request.POST.get("rmi"))
    rmf = int(request.POST.get("rmf"))
    buffer = BytesIO()
    buffer = emitir_lista_rm(rmi, rmf, buffer)
    
    nome_arquivo = str(rmi) + '_' + str(rmf) + datetime.strftime(datetime.now(),'_%d/%m/%Y_%H_%M_%S')
    response = HttpResponse(content_type='application/pdf')
    
    response['Content-Disposition'] = (
        f'attachment; filename={nome_arquivo}.pdf')
    
    response.write(buffer.getvalue())
    buffer.close()
    
    return response


def baixar_lista_telefonica(request):
    
    classe = Classe.objects.get(pk=int(request.POST.get("classe")))
    buffer = BytesIO()   
    buffer = emitir_lista_telefonica(classe, buffer)
    nome_arquivo = str(classe) + datetime.strftime(datetime.now(),'_%d/%m/%Y_%H_%M_%S')
    response = HttpResponse(content_type='application/pdf')
    
    response['Content-Disposition'] = (
        f'attachment; filename={nome_arquivo}.pdf')
    
    response.write(buffer.getvalue())
    buffer.close()
    
    return response


def baixar_lista_alunos_personalizada(request):
    
    titulo_lista = request.POST.get('titulo')
    tamanho_fonte = float(request.POST.get('tamanho_fonte'))
    colunas = (request.POST.get('colunas')).split(',')
    tamanho_colunas = (request.POST.get('tam_colunas')).split(',')
    orientacao = request.POST.get('pagina')
    repeticao = int(request.POST.get('repeticao'))
    classe = Classe.objects.get(pk=int(request.POST.get("classe")))
    buffer = BytesIO()

    
    buffer = emitir_lista_personalizada(classe, titulo_lista, tamanho_fonte, colunas, 
                                        tamanho_colunas, orientacao, repeticao, buffer)



    response = HttpResponse(content_type='application/pdf')
    
    response.write(buffer.getvalue())
    buffer.close()
    
    return response

