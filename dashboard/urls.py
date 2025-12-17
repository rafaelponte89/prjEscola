from django.urls import path

from .views import dashboard, visualizar_alunos_mes, visualizar_alunos_periodo

urlpatterns = [
    path('dashboard', dashboard, name='dashboard'),
    path('visperiodo', visualizar_alunos_periodo, name='visperiodo'),
    path('visqtdalunos', visualizar_alunos_mes, name='visqtdalunos')

]