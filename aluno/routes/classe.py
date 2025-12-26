from django.urls import path

from aluno.views.classe import (atualizar, buscar_classe, classe, deletar, exibirClasse,
                    exibirQuadro, gerarTurmas, gravar, listar_classe)

urlpatterns = [
    path('', classe, name='classe'),
    path('gravarclasse', gravar, name='gravarclasse'),
    path('atualizarclasse', atualizar, name='atualizarclasse'),
    path('deletarclasse', deletar, name='deletarclasse'),
    path('listarclasse', listar_classe, name='listarclasse'),
    path('buscarclasse', buscar_classe, name='buscarclasse'),
    path('exibirQuadro', exibirQuadro, name='exibirQuadro'),
    path('gerarTurmas', gerarTurmas, name='gerarTurmas'),
    
   
    path('exibirClasse', exibirClasse, name='exibirClasse'),
    
]