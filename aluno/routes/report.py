from django.urls import path
from aluno.views.report import baixar_declaracao_matricula, baixar_lista_telefonica, baixar_pdf

urlspatterns = [
    path("baixardeclaracao", baixar_declaracao_matricula, name="baixar_declaracao_matricula"),
    path("baixarpdf", baixar_pdf, name="baixarpdf"),
    path("listatelefonicapdf", baixar_lista_telefonica, name='listatelefonicapdf'),
   
]
