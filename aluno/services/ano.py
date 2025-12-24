from aluno.models.ano import Ano

def retornarStatusAno(ano):
    ano = Ano.objects.get(pk=ano)
    if ano.fechado:
        return '<i class="bi bi-lock-fill"></i>'
    else:
        return '<i class="bi bi-unlock-fill"></i>'