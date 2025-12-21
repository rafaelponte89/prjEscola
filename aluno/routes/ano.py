from django.urls import path

from aluno.views.ano import (buscar_ano, excluir_ano, fechar_abrir_ano, gravar_ano,
                    inicial_ano, listar_ano, selecionar_ano, status_ano)

urlpatterns = [
    path("gravarano", gravar_ano, name="gravarano"),  
    path("fecharabrirano", fechar_abrir_ano, name="fecharabrirano"),
    path("statusano", status_ano, name="statusano"),
    path("", inicial_ano, name="ano"),
    path("listarano", listar_ano, name="listarano"),
    path("buscarano", buscar_ano, name="buscarano"),
    path("excluirano", excluir_ano, name="excluirano"),
    path("selecionarano", selecionar_ano, name="selecionarano")

]