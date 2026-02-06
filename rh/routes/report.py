
from django.urls.conf import path

from rh.views.registro_falta import (
                    emitir_abonada, gerar_requerimento_abono_pdf,
                    relatorio_faltas,
                    relatorio_faltas_descritivo,
                    relatorio_faltas_descritivo_pdf, relatorio_faltas_geral)

urlpatterns = [ path('relatorio-faltas/<str:pessoa_id>/', relatorio_faltas, name='relatorio_faltas_pessoa'),
    path('relatorio-faltas/', relatorio_faltas_geral, name='relatorio_faltas_geral'),
    path('relatorio-faltas-descritivo/', relatorio_faltas_descritivo, name='relatorio_faltas_descritivo'),
    path('relatorio-faltas-descritivo/pdf/', relatorio_faltas_descritivo_pdf, name='relatorio_faltas_descritivo_pdf'),
    #path('relatorio-faltas/pdf/', views.relatorio_faltas_pdf, name='relatorio_faltas_pdf'),
    path('relatorio-faltas-requerimento/<str:servidor_id>/pdf/<int:ano>', gerar_requerimento_abono_pdf, name='gerar_requerimento_abono_pdf'),
    path('requerimento-abonada/pdf/<int:lancamento_id>', emitir_abonada, name='emitirabonada'),
]