import re
from django import template

register = template.Library()

@register.filter
def formatar_telefone(valor):
    if not valor:
        return ""

    # Remove tudo que não for número
    numero = re.sub(r"\D", "", valor)

    # Celular com DDD (11 dígitos)
    if len(numero) == 11:
        return f"({numero[:2]}) {numero[2:7]}-{numero[7:]}"

    # Fixo com DDD (10 dígitos)
    if len(numero) == 10:
        return f"({numero[:2]}) {numero[2:6]}-{numero[6:]}"

    return valor
