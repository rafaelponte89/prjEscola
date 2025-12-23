from .routes import aluno, classe, matricula, ano, dashboard, report # Importando seus arquivos da pasta urls
from django.urls import path, include

urlpatterns = [
    path('aluno/', include(aluno.urlpatterns)),
    path('classe/', include(classe.urlpatterns)),
    path('matricula/', include(matricula.urlpatterns)),
    path('ano/', include(ano.urlpatterns)),
    path('dashboard/', include(dashboard.urlpatterns)),
    path('report/', include(report.urlspatterns))


]