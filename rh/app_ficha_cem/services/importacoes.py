import re
import pdfplumber
from datetime import datetime
from rh.app_ficha_cem.models import Faltas_Pessoas
from rh.models.falta import Faltas
from rh.models.pessoa import Pessoas
from django.db import transaction, IntegrityError

def ignorar_linhas(linha):
    
    return (
        not linha.strip() or
        "Relação de Afastamentos" in linha or
        "PREFEITURA MUNICIPAL" in linha or
        "Protocolo:" in linha or
        "Página:" in linha or
        "Data:" in linha or
        "Parâmetros:" in linha
    )
          
def extrair_matricula(linha):
    padrao = re.search(r"(\d+)/(\d+)", linha)
    if padrao:
        return padrao.group(1)
    
    return None

def extrair_data_inicial(linha):
    datas = re.search(r"\d{2}/\d{2}/\d{4}", linha)
    print(datas)
    if datas:
        return datetime.strptime(datas.group(0), "%d/%m/%Y").date()
    return None

def extrair_quantidade_dias(linha):
    padrao = re.search(r"(\d+)\s+dia\(s\)", linha)
    if padrao:
        return int(padrao.group(1))
    return None

def extrair_tipo_falta(linha):
    padrao = re.search(r"\d+\s+dia\(s\)\s+(.*)$", linha)
    if padrao:
        return padrao.group(1).strip()
    return None

def converter_tipo_falta(tipo_falta):
    
    TIPOS_FALTAS = {
        "MÉDICO": "AM",
        "ODONTOLÓGICO": "AO",
        "FÉRIAS": "F",
        "ABONADA": "AB",
        }
    
    if tipo_falta is None:
        return None
    
    for chave, valor in TIPOS_FALTAS.items():
        if chave in tipo_falta.upper():
            return valor
        
def processar_linha(linha):
    if ignorar_linhas(linha):
        return None
    
    matricula = extrair_matricula(linha)
    data_inicial = extrair_data_inicial(linha)  
    dias = extrair_quantidade_dias(linha)
    tipo_falta = converter_tipo_falta(extrair_tipo_falta(linha))
    
    if matricula and data_inicial and dias:
        return {
            "matricula": matricula,
            "data_inicial": data_inicial,
            "quantidade_dias": dias,
            "tipo_falta": tipo_falta
        }
    return None

def extrair_afastamentos_pdf(caminho_pdf):
    resultados = []
    
    with pdfplumber.open(caminho_pdf) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            for linha in texto.split("\n"):
                dado = processar_linha(linha)
            
                if dado:
                    resultados.append(dado)
            
            print("=" * 80)
    return resultados

def importar_afastamentos_pdf(caminho_pdf):
    registros = extrair_afastamentos_pdf(caminho_pdf)
    objetos = []


    for r in registros:
        try:
            print("cheguei aqui")
            pessoa = Pessoas.objects.get(id=r["matricula"])
            print("Nome:", pessoa.nome)
            print("Registros:", r)
            
            falta = Faltas.objects.filter(tipo= r["tipo_falta"]).first()
            print('Falta:', falta.descricao)
            objetos.append(
                Faltas_Pessoas(
                    pessoa=pessoa,
                    data=r["data_inicial"],
                    falta=falta,
                    qtd_dias=r["quantidade_dias"]
                )
            )
        except Exception:
            return {
                "status": "erro",
                "mensagem": "Erro ao preparar dados do PDF"
            }

    try:
      
        with transaction.atomic():
            Faltas_Pessoas.objects.bulk_create(objetos)
    except IntegrityError:
        return {
            "status": "erro",
            "mensagem": "Erro de integridade (registro duplicado)"
        }

    return {
        "status": "ok",
        "importados": len(objetos)
    }