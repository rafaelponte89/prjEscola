from django.urls import path
from .views import (adicionar, deletar, matricula, 
                    ordernar_alfabetica, carregar_matriculas,
                    buscar_matricula, excluir_matricula, movimentar, carregar_classes_remanejamento,
                    upload_matriculas, carregar_movimentacao, buscarAluno, adicionarNaClasse,exibirTelaMatricula, matricular_aluno_ia)

urlpatterns = [
    path('matricula', matricula, name='matricula'),
    path('adicionar', adicionar, name='adicionar'),
    path('deletar', deletar, name='deletar'),
    path('ordenarAlfabeto', ordernar_alfabetica, name='ordemalfabetica'),
   # path('carregarClasses', carregar_classes, name='carregarclasses'),
    path('carregarClassesRemanejamento', carregar_classes_remanejamento, name='carregarclassesremanejamento'),
    path('carregarMovimentacao', carregar_movimentacao, name='carregarmovimentacao'),
    path('carregarMatriculas', carregar_matriculas, name='carregarmatriculas'),
    path('buscarMatricula', buscar_matricula, name='buscarmatricula'), 
    path('excluirMatricula', excluir_matricula, name='excluirmatricula'),
    path('movimentar', movimentar, name='movimentar'),
    path('uploadMatriculas', upload_matriculas, name='uploadmatriculas'),


    path('buscarAluno', buscarAluno, name='buscarAluno'),
    path('adicionarNaClasse', adicionarNaClasse, name='adicionarNaClasse'),
    path('telamatricular', exibirTelaMatricula, name='telamatricular'),
    path('matricular_aluno_ia', matricular_aluno_ia, name='matricular_aluno_ia')

]