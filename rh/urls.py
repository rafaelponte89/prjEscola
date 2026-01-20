from django.urls.conf import include, path

from rh.views.registro_falta import index

from .routes import falta, cargo, pessoa, pontuacao, registro_falta

urlpatterns = [
    path('',index, name='index'),
    path('falta/', include(falta.urlpatterns)),
    path('cargo/',include(cargo.urlpatterns)),
    path('pontuacao/', include(pontuacao.urlpatterns)),
    path('pessoa/',include(pessoa.urlpatterns)),
    path('fichacem/', include(registro_falta.urlpatterns))

 
]