from django.urls import path
from aluno.views.telefone import bloco_contato, buscar_telefones_aluno, del_telefone, descrever_contato

urlspatterns = [
    path("bloco_contato", bloco_contato, name="bloco_contato"),
    path("buscarTelefonesAluno", buscar_telefones_aluno, name="buscarTelefonesAluno"),
    
    
    path("delTelefone", del_telefone, name="delTelefone"),
    path("contato", descrever_contato, name="contato"),
   
]