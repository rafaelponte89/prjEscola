from django.urls import path
from aluno.views.telefone import bloco_contato, del_telefone

urlspatterns = [
    path("bloco_contato", bloco_contato, name="bloco_contato"),
    path("delTelefone", del_telefone, name="delTelefone"),
   
]