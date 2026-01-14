from aluno.services.telefone import buscar_telefones
from aluno.models.telefone import Telefone
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string

        
def del_telefone(request):
    id_tel = request.POST.get('id_tel')
    telefone = Telefone.objects.get(pk=id_tel)
    telefone.delete()
    return HttpResponse("Telefone Excluido")

def bloco_contato(request):
    rm = request.GET.get("rm")
    telefones = buscar_telefones(rm) if rm else []

    html = render_to_string(
        "aluno/aluno/partials/dados_contato.html",
        {
            "telefones": telefones,
            "tel_choices": Telefone.TEL_CHOICES,
        },
        request=request
    )

    return JsonResponse({"html": html})
