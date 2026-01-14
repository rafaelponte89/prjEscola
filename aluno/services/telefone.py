from aluno.models.aluno import Aluno
from aluno.models.telefone import Telefone

def buscar_telefones(rm):
    aluno = Aluno.objects.get(pk=rm)
    return Telefone.objects.filter(aluno=aluno)