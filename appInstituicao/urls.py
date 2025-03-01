from django.urls import path
from .views import (instituicao, gravar_instituicao, pesquisar_instituicao, 
                    excluir_instituicao, carregar_instituicoes)


urlpatterns = [
    path('instituicao', instituicao, name='instituicao'),
    path('gravar_instituicao', gravar_instituicao, name='gravar_instituicao'),
    path('pesquisar_instituicao', pesquisar_instituicao, name='pesquisar_instituicao'),
    path('excluir_instituicao', excluir_instituicao, name='excluir_instituicao' ),
    path('carregar_instituicoes', carregar_instituicoes, name='carregar_instituicoes')
]