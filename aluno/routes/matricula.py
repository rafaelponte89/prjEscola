from django.urls import path, include

from aluno.views.matricula import (adicionarNaClasse, buscar_matricula,
                    buscarAluno, carregar_classes_remanejamento,
                    carregar_matriculas, carregar_movimentacao,
                    excluir_matricula, exibirTelaMatricula, matricula,
                    matricular_aluno_ia, movimentar, ordenar_em_alfabetica,
                    upload_matriculas, buscar_historico_matricula)
urlpatterns = [
    path('', matricula, name='matricula'),
    path('ordenarAlfabeto', ordenar_em_alfabetica, name='ordemalfabetica'),
    path('carregarClassesRemanejamento', carregar_classes_remanejamento, name='carregarclassesremanejamento'),
    path('carregarMovimentacao', carregar_movimentacao, name='carregarmovimentacao'),
    path('carregarMatriculas', carregar_matriculas, name='carregarmatriculas'),
    path('buscarMatricula', buscar_matricula, name='buscarmatricula'), 
    path('excluirMatricula', excluir_matricula, name='excluirmatricula'),
    path('movimentar', movimentar, name='movimentar'),
    path('importarMatriculas', upload_matriculas, name='uploadmatriculas'),
    path('buscarAluno', buscarAluno, name='buscaraluno'),
    path('adicionarNaClasse', adicionarNaClasse, name='adicionarnaclasse'),
    path('telamatricular', exibirTelaMatricula, name='telamatricular'),
    path('matricular_aluno_ia', matricular_aluno_ia, name='matricular_aluno_ia'),
    path("buscar_historico_matricula",buscar_historico_matricula, name="buscar_historico_matricula"),

]