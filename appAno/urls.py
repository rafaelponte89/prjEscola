from django.urls import path
from .views import (gravar_ano, fechar_abrir_ano, status_ano,
                    inicial_ano, listar_ano,buscar_ano, excluir_ano, selecionar_ano)

urlpatterns = [
    path("gravarano", gravar_ano, name="gravarano"),  
    path("fecharabrirano", fechar_abrir_ano, name="fecharabrirano"),
    path("statusano", status_ano, name="statusano"),
    path("ano", inicial_ano, name="ano"),
    path("listarano", listar_ano, name="listarano"),
    path("buscarano", buscar_ano, name="buscarano"),
    path("excluirano", excluir_ano, name="excluirano"),
    path("selecionarano", selecionar_ano, name="selecionarano")

]