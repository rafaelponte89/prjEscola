from django.urls.conf import path

from rh.views.pontuacao import lancar_pontuacoes, atualizar_pontuacoes, excluir_pontuacoes

urlpatterns = [
    path('salvar/<str:pessoa_id>', lancar_pontuacoes, name='lancarpontuacao'),
    path('editar/<str:pessoa_id>/<int:pontuacao_id>', atualizar_pontuacoes, name='atualizarpontuacao'),
    path('deletar/<str:pessoa_id>/<int:pontuacao_id>', excluir_pontuacoes, name='excluirpontuacao'),
 ]





