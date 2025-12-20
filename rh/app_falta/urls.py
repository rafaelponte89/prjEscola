from django.urls.conf import path

from .views import atualizar_faltas, faltas

urlpatterns = [
          path('', faltas, name='listarfaltas'),
          path('<int:falta_id>', atualizar_faltas, name='atualizarfaltas' )
]