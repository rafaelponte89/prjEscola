from django import template

register = template.Library()
CSS_STATUS = {
    "C": "text-primary",
    "BXTR": "text-danger",
    "TRAN": "text-danger",
    "REMA": "text-success",
    "P": "text-primary",
    "R": "text-danger",
    "NCFP": "text-danger",
}

@register.filter
def css_situacao(situacao):
    return CSS_STATUS.get(situacao, "text-dark")


@register.filter
def data_br(data):
    if not data:
        return "—"
    return data.strftime("%d/%m/%Y")


@register.filter
def descricao_situacao(descricao):
    DESCRICOES = {
        "C": "CURSANDO",
        "BXTR": "TRANSFERIDO",
        "TRAN": "TRANSFERIDO",
        "REMA": "REMANEJADO",
        "P": "PROMOVIDO",
        "R": "REPROVADO",
        "NCFP": "Ñ COMP. FORA PRAZO",
    }
    return DESCRICOES.get(descricao, "DESCONHECIDO")