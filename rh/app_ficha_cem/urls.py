from django.urls.conf import include, path

from .views import (abrir_ano, coletivo, encerrar_ano_v2,
                    excluir_pessoas_faltas, gerar_ficha,
                    emitir_abonada, gerar_requerimento_abono_pdf,
                    lancar_evento_coletivo, listar_ficha,
                    pdf_v3, pessoas_faltas, relatorio_faltas,
                    relatorio_faltas_descritivo,
                    relatorio_faltas_descritivo_pdf, relatorio_faltas_geral,
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
    path('relatorio-faltas/<str:pessoa_id>/', relatorio_faltas, name='relatorio_faltas_pessoa'),
    path('relatorio-faltas/', relatorio_faltas_geral, name='relatorio_faltas_geral'),
    path('relatorio-faltas-descritivo/', relatorio_faltas_descritivo, name='relatorio_faltas_descritivo'),
    path('relatorio-faltas-descritivo/pdf/', relatorio_faltas_descritivo_pdf, name='relatorio_faltas_descritivo_pdf'),
    #path('relatorio-faltas/pdf/', views.relatorio_faltas_pdf, name='relatorio_faltas_pdf'),
    path('relatorio-faltas-requerimento/<str:servidor_id>/pdf/<int:ano>', gerar_requerimento_abono_pdf, name='gerar_requerimento_abono_pdf'),
    path('requerimento-abonada/pdf/<int:lancamento_id>', emitir_abonada, name='emitirabonada'),
    path("ferramentas/importar-afastamentos", importar_afastamentos, name="importar_afastamentos"),



]