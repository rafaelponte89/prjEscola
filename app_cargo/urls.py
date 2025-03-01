from django.urls.conf import path
from .views import cargos, atualizar_cargos

urlpatterns = [
     path('', cargos, name='listarcargos'),
     path('<int:cargo_id>', atualizar_cargos, name='atualizarcargos' )

]