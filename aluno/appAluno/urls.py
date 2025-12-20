from django.urls import path

from utilitarios.utilitarios import realizar_backup_v2

from .views import (atualizar, baixar_declaracao,
                    baixar_lista_alunos_personalizavel,
                    baixar_lista_telefonica, baixar_pdf, buscar,
                    buscar_dados_aluno, buscar_historico_matriculas,
                    buscar_telefones_aluno, buscarRMCancelar, cancelarRM,
                    carregar_classes, del_telefone, descrever_contato, gravar,
                    index, recarregarTabela)

urlpatterns = [
    path("", index, name="inicial"),  
    path("gravar", gravar, name="gravar"),
    path("buscar", buscar, name="buscar"),
    
    #path("buscarRM", buscarRM, name ="buscarRM"), # em desenvolvimento
    path("buscarDadosAluno", buscar_dados_aluno, name="buscarDadosAluno"), # em desenvolvimento

    path("buscarRMCancelar", buscarRMCancelar, name="buscarRMCancelar"), # em desenvolvimento
    path("recarregarTabela", recarregarTabela, name="recarregarTabela"),
    path("atualizar", atualizar, name="atualizar"),
    path("cancelarRM", cancelarRM, name="cancelarRM"), # em desenvolvimento
    path("baixarpdf", baixar_pdf, name="baixarpdf"),
    path("listatelefonicapdf", baixar_lista_telefonica, name='listatelefonicapdf'),
    path("listapersonalizavelpdf", baixar_lista_alunos_personalizavel, name='listapersonalizavelpdf'),
    path("baixardeclaracao", baixar_declaracao, name="baixardeclaracao"),

    
    path("bkp", realizar_backup_v2, name="realizarbackup"),
    path("carregarClasses", carregar_classes, name="carregarclasses"),
    
    path("delTelefone", del_telefone, name="delTelefone"),
    path("contato", descrever_contato, name="contato"),
    
    # Em desenvolvimento 10052024
    path("buscarHistoricoMatriculas",buscar_historico_matriculas, name="buscarHistoricoMatriculas"),
    path("buscarTelefonesAluno", buscar_telefones_aluno, name="buscarTelefonesAluno")
]