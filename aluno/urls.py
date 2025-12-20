from django.urls import include, path


urlpatterns = [
    path('', include('aluno.appAluno.urls')),
    path('', include('aluno.appClasse.urls')),
    path('', include('aluno.appMatricula.urls')),
    path('', include('aluno.dashboard.urls')),
    path('', include('aluno.appAno.urls')),
    path('', include('aluno.appInstituicao.urls')),
    ]