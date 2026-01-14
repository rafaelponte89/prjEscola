from django.urls import path

from utilitarios.utilitarios import realizar_backup_v2

from aluno.views.aluno import (atualizar_aluno,
                    pesquisar_aluno,
                    buscar_dados_aluno,
                    buscarRMCancelar, cancelarRM, salvar_aluno,
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
    
    
]