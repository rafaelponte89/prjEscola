from django.urls.conf import include, path

from rh.views.registro_falta import index_rh

from .routes import falta, cargo, pessoa, pontuacao, registro_falta

from django.urls import path, include
from rh.views.registro_falta import index_rh
from .routes import falta, cargo, pessoa, pontuacao, registro_falta

urlpatterns = [
    path('', index_rh, name='index_rh'),  # Página inicial do RH
    path('falta/', include(falta.urlpatterns)),
    path('cargo/', include(cargo.urlpatterns)),
    path('pontuacao/', include(pontuacao.urlpatterns)),
    path('pessoa/', include(pessoa.urlpatterns)),
    path('fichacem/', include(registro_falta.urlpatterns)),
]
