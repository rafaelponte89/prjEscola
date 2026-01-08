from aluno.models.aluno import Aluno
from aluno.models.telefone import Telefone
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string


def buscar_telefones_aluno(request):
    rm = request.POST.get('rm')
    aluno = Aluno.objects.get(pk=rm)
    telefones = Telefone.retornarListaTelefones()
    telefones_aluno = Telefone.objects.filter(aluno=aluno)
    selecionado = "" 
    adicionar_tel = """<div class="row">
               <div class="col-1 form-group d-flex">
                  <button id="addTelefone" type="button" class="btn btn-primary mt-3"><i class="bi bi-telephone-plus"></i></button>
                </div>
            </div>"""
    
    def retornar_telefone( telefones_aluno):  
        selecionado_tel = ""     
        opcoes_telefone = f"<option {selecionado}> Selecione </option>"
        for tel in telefones:
            sigla, contato = tel
            if telefones_aluno.contato == sigla:
                selecionado_tel = "selected"
                opcoes_telefone += f"""<option value={sigla} {selecionado_tel}>{contato}</option>"""
            else:
                
                opcoes_telefone += f"""<option value='{sigla}'>{contato}</option>"""
        return opcoes_telefone   

    dados_telefone = "" 
    for i in range(len(telefones_aluno)):  
        dados_telefone += f"""
                   <div class="col-12 form-group d-flex align-items-center"> 
                  <input        
                    type="number"     
                    class="form-control numTelefone p-2" 
                    id="telefoneAtualizar" 
                    aria-describedby="emailHelp" 
                    placeholder="Telefone" 
                    value="{telefones_aluno[i].numero}"
                  /> 
                      <select class="form-select m-3 contato" aria-label="Default select example" class="linhaTelefone"> 
                        {retornar_telefone(telefones_aluno[i])}
                    </select> 
                   <button type="button" class="btn btn-danger m-1 removerTelefone" value="{telefones_aluno[i].id}"><i class="bi bi-telephone-minus"></i></button> 
                </div>"""

    dados_telefone = adicionar_tel + dados_telefone
    return HttpResponse(dados_telefone)

def descrever_contato(request):
    contatos = Telefone.retornarListaTelefones()
    opcao = "<option value='0'>Selecione </option>"
    for i in contatos:
        sigla, contato = i
        opcao += f"""<option value='{sigla}'>{contato}</option>"""
        
    novoTelefone  = f"""<div class="col-12 form-group d-flex align-items-center"> 
                  <input        
                    type="number"     
                    class="form-control numTelefone p-2" 
                    id="telefoneAtualizar" 
                    aria-describedby="emailHelp" 
                    placeholder="Telefone" 
                  /> 
                  <select class="form-select m-3 contato" aria-label="Default select example">
                    {opcao}
                    </select>
                   <button type="button" class="btn btn-danger m-1 removerTelefone" value="0"><i class="bi bi-telephone-minus"></i></button>\
                </div>"""
                
    return HttpResponse(novoTelefone)
        
def del_telefone(request):
    id_tel = request.POST.get('id_tel')
    telefone = Telefone.objects.get(pk=id_tel)
    telefone.delete()
    return HttpResponse("Telefone Excluido")


def buscar_telefones(rm):
    aluno = Aluno.objects.get(pk=rm)
    return Telefone.objects.filter(aluno=aluno)
        
    

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
