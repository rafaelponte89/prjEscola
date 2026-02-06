from django.urls.conf import path

from rh.views.registro_falta import (abrir_ano, coletivo, encerrar_ano_v2,
                    excluir_pessoas_faltas, gerar_ficha,
                    lancar_evento_coletivo, listar_ficha,
                    pdf_v3, pessoas_faltas, 
                    importar_afastamentos)

urlpatterns = [
    path('<str:pessoa_id>/faltas', pessoas_faltas, name="lancarfalta" ),
    path('pessoas/<str:pessoa_id>/faltas/<int:lancamento_id>', excluir_pessoas_faltas, name="excluirevento" ),
    path('pessoas/<str:pessoa_id>/fichas', listar_ficha, name='listarficha' ),
    path('pessoas/<str:pessoa_id>/fichas/<int:ano>', gerar_ficha, name='ficha'),
    path('pessoas/<str:pessoa_id>/fichas/encerrar/<int:ano>', encerrar_ano_v2, name='encerrarano' ),
    path('pessoas/<str:pessoa_id>/fichas/abrir/<int:ano>', abrir_ano, name='abrirano' ),
    path('pessoas/<str:pessoa_id>/fichaspdf/<int:ano>/', pdf_v3, name='baixarpdf'),
    path('coletivo', coletivo, name='coletivo'),
    path('coletivo/evento', lancar_evento_coletivo, name='eventocoletivo'),
    path("ferramentas/importar-afastamentos", importar_afastamentos, name="importar_afastamentos"),
]