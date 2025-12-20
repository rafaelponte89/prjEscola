from django.urls.conf import include, path

from rh.app_ficha_cem.views import index

urlpatterns = [
    path('',index, name='index'),
    path('faltas/', include('rh.app_falta.urls')),
    path('cargos/',include('rh.app_cargo.urls')),
    path('fichacem/', include('rh.app_ficha_cem.urls')),
    path('pontuacoes/', include('rh.app_pontuacao.urls')),
    path('pessoas/',include('rh.app_pessoa.urls')),
 
]