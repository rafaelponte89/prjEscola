from django.urls import path
from .views import dashboard, visualizar_alunos_periodo, visualizar_alunos_mes

urlpatterns = [
    path('dashboard', dashboard, name='dashboard'),
    path('visperiodo', visualizar_alunos_periodo, name='visperiodo'),
    path('visqtdalunos', visualizar_alunos_mes, name='visqtdalunos')

]