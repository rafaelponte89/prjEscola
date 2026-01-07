from django.urls import path

from aluno.views.classe import (atualizar, buscar_classe, classe, deletar, exibirClasse,
                    exibirQuadro, gerarTurmas, gravar, listar_classe,
                    carregar_classes)

urlpatterns = [
    path('', classe, name='classe'),
    path('gravarclasse', gravar, name='gravar_classe'),
    path('atualizarclasse', atualizar, name='atualizar_classe'),
    path('deletarclasse', deletar, name='deletar_classe'),
    path('listarclasse', listar_classe, name='listar_classe'),
    path('buscarclasse', buscar_classe, name='buscar_classe'),
    path('exibirQuadro', exibirQuadro, name='exibir_quadro'),
    path('gerarTurmas', gerarTurmas, name='gerar_turmas'),

   
    path('exibirClasse', exibirClasse, name='exibir_classe'),
    path("carregarClasses", carregar_classes, name="carregarclasses"),

    
]