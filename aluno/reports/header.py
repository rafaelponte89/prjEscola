
from reportlab.platypus import Image
from reportlab.lib.pagesizes import A4


def header_com_imagem(
    canvas,
    doc,
    caminho_imagem,
    largura=500,
    altura=120,
    margem_topo=20,  # distância do topo da página
):
    canvas.saveState()

    largura_pagina, altura_pagina = doc.pagesize

    x = (largura_pagina - largura) / 2
    y = altura_pagina - altura - margem_topo

    img = Image(caminho_imagem, width=largura, height=altura)
    img.drawOn(canvas, x, y)

    canvas.restoreState()
