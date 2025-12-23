from django.urls import path

from utilitarios.utilitarios import realizar_backup_v2

from aluno.views.aluno import (atualizar_aluno,
                    baixar_lista_alunos_personalizavel, pesquisar_aluno,
                    buscar_dados_aluno, buscar_historico_matriculas,
                    buscar_telefones_aluno, buscarRMCancelar, cancelarRM,
                    carregar_classes, del_telefone, descrever_contato, salvar_aluno,
                    index, recarregarTabela)

urlpatterns = [
    path("", index, name="inicial"),  
    path("salvar", salvar_aluno, name="salvar_aluno"),
    path("buscarDadosAluno", buscar_dados_aluno, name="buscarDadosAluno"), 
    path("atualizar", atualizar_aluno, name="atualizar"),
    path("pesquisar", pesquisar_aluno, name="pesquisar_aluno"),
    path("buscarRMCancelar", buscarRMCancelar, name="buscarRMCancelar"), 
    path("recarregarTabela", recarregarTabela, name="recarregarTabela"),
    path("cancelarRM", cancelarRM, name="cancelarRM"), 
    
    path("bkp", realizar_backup_v2, name="realizarbackup"),
    path("carregarClasses", carregar_classes, name="carregarclasses"),
    
    path("delTelefone", del_telefone, name="delTelefone"),
    path("contato", descrever_contato, name="contato"),
    
    # Em desenvolvimento 10052024
    path("buscarHistoricoMatriculas",buscar_historico_matriculas, name="buscarHistoricoMatriculas"),
    path("buscarTelefonesAluno", buscar_telefones_aluno, name="buscarTelefonesAluno"),
    
    path("listapersonalizavelpdf", baixar_lista_alunos_personalizavel, name='listapersonalizavelpdf'),
    #path("baixardeclaracao", baixar_declaracao_matricula, name="baixardeclaracao"),
]