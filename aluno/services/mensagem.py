
from django.template.loader import render_to_string

def criarMensagemJson(texto, tipo):
    return render_to_string('aluno/mensagem.html', {
        'texto': texto,
        'tipo': tipo
    })