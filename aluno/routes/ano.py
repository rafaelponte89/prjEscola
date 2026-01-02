from django.urls import path

from aluno.views.ano import (buscar_ano, excluir_ano, fechar_abrir_ano, gravar_ano,
                    inicial_ano, listar_ano, selecionar_ano, status_ano)

urlpatterns = [
    path("gravarano", gravar_ano, name="gravar_ano"),  
    path("fecharabrirano", fechar_abrir_ano, name="fechar_abrir_ano"),
    path("statusano", status_ano, name="status_ano"),
    path("", inicial_ano, name="ano"),
    path("listarano", listar_ano, name="listar_ano"),
    path("buscarano", buscar_ano, name="buscar_ano"),
    path("excluirano", excluir_ano, name="excluir_ano"),
    path("selecionarano", selecionar_ano, name="selecionar_ano")

]