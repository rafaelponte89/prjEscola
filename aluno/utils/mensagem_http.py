from django.http import HttpResponse

def criarMensagemModal(texto, tipo):
    mensagem = HttpResponse(f"<div style='display:block;' id='mensagemModal' class='alert alert-{tipo}' role='alert' >{texto} </div>")
    return  mensagem