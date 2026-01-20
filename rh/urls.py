from django.urls.conf import include, path

from rh.app_ficha_cem.views import index

from .routes import falta, cargo, pessoa, pontuacao

urlpatterns = [
    path('',index, name='index'),
    path('falta/', include(falta.urlpatterns)),
    path('cargo/',include(cargo.urlpatterns)),
    path('pontuacao/', include(pontuacao.urlpatterns)),
    path('pessoa/',include(pessoa.urlpatterns)),
    
    path('fichacem/', include('rh.app_ficha_cem.urls')),

 
]