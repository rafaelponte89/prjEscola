from email.mime import image
import os
from django.conf import settings


def obter_caminho_imagem_cabecalho():
    return os.path.join(
    settings.BASE_DIR,
    'aluno',
    'static',
    'aluno',
    'jpeg',
    'cabecalho_600dpi.png'
    )