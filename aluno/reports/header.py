
from reportlab.platypus import Image
from reportlab.lib.pagesizes import A4


def header_com_imagem(
    canvas,
    doc,
    caminho_imagem,
    largura=500,
    altura=120,
    margem_y=150,
):
    """
    Cabeçalho padrão com imagem.
    """
    canvas.saveState()

    img = Image(caminho_imagem, width=largura, height=altura)
    img.drawOn(canvas, doc.leftMargin, A4[1] - margem_y)

    canvas.restoreState()