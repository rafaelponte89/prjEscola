
from django.urls import path

from .views import (atualizar_pessoa, cadastrar_pessoas, pesquisar_pessoas,
                    selecionar_pessoa, tela_pesquisar_pessoas)

urlpatterns = [
    path('cadastrarpessoas', cadastrar_pessoas, name="cadastrarpessoas"),
    path('telapesquisar',tela_pesquisar_pessoas, name="telapesquisarpessoas"),
    path('pesquisar/',pesquisar_pessoas, name="pesquisarpessoas"),
    path('atualizarpessoa/<str:pessoa_id>', atualizar_pessoa, name="atualizarpessoa"),
    path('selecao/pessoa', selecionar_pessoa, name='selecionarpessoa')
]