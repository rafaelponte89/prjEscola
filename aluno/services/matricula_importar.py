import pdfplumber
import re
from aluno.models.aluno import Aluno
from aluno.models.matricula import Matricula
from aluno.models.classe import Classe
from aluno.models.ano import Ano
from django.db import transaction, IntegrityError
from datetime import datetime
from aluno.services.matricula import deletar_todas_matriculas_da_classe, verificar_matricula_ativa_no_ano
from aluno.services.mensagem import criarMensagemJson

def ignorar_linhas(linha):
    termos_ignorados = [
        "Relação de Alunos por Classe",
        "Escola:",
        "Tipo Ensino:",
        "Turma:",
        "Ativos:",
        "Série",
    ]
    return any(termo in linha for termo in termos_ignorados)
    

def extrair_data_mov(linha):
    padrao = re.search(r'(?:TRAN)\s+(\d{2}/\d{2}/\d{4})', linha)
       
    if padrao:
        return padrao.group(1)
    
    return None

def extrair_ra(linha):
    
    padrao = re.search(r"\b(?P<ra>\d{10,13})\s+(?P<digito>[0-9X])\s+(?P<uf>[A-Z]{2})\b",linha)

    if padrao:
        return padrao.group(1).lstrip("0")
    return None

def extrair_situacao(linha):
    padrao = re.search(r'\b\d{2}/\d{2}/\d{4}\b\s+([A-Z]+)\s+\b\d{2}/\d{2}/\d{4}\b', linha)
    if padrao:
        return padrao.group(1)
    
    return None

def processar_linha(linha):
    if ignorar_linhas(linha):
        return None
    
    ra = extrair_ra(linha)
    situacao = extrair_situacao(linha)
    data_mov = extrair_data_mov(linha)
    numero_aluno = extrair_numero_aluno(linha)
    
    return {
        "ra": ra,
        "situacao": situacao,
        "data_mov": data_mov,
        "numero_aluno": numero_aluno
    }

def extrair_numero_aluno(linha):
    padrao = re.match(r"\d+\s+(\d+)\s+(.+)", linha)
    if padrao:
        return padrao.group(1)
    return None

def extrair_matriculas_pdf(caminho_pdf):
    
    resultado = []
    with pdfplumber.open(caminho_pdf) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if texto:
                for linha in texto.split("\n"):
                    if not ignorar_linhas(linha):
                        dados = processar_linha(linha)
                    
                        if dados["ra"] is not None:
                            resultado.append(dados)
    return resultado

def importar_matriculas_pdf(caminho_pdf, classe, ano, data_matricula):
    registros = extrair_matriculas_pdf(caminho_pdf)
   
    objetos = []
    classe = Classe.objects.get(pk=classe)
    ano = Ano.objects.get(pk=ano)
    
    for r in registros:
        try:
            
            aluno = Aluno.objects.filter(ra=r["ra"]).first()
            matricula = Matricula.objects.filter(aluno=aluno, ano=ano, situacao__in=['C']).first()
            matricula.delete() if matricula else None
            if not aluno:
                continue
            
            aluno.status = Aluno.STATUS_ATIVO
            aluno.save()
            ano = ano
            data_matricula = data_matricula
            situacao = r["situacao"] if r["situacao"] is not None else 'C'
            data_mov = datetime.strptime(r["data_mov"], "%d/%m/%Y").date() if r["data_mov"] else None
            numero = r["numero_aluno"]
            objetos.append(
                Matricula(aluno=aluno, situacao=situacao, data_movimentacao=data_mov, classe=classe, ano=ano, data_matricula=data_matricula, numero = numero)
            )
        except Exception as e:
        
            return {
                "status": "erro",
                "mensagem": criarMensagemJson(f"Erro ao preparar dados do PDF: {e}", "danger")
            }

    try:
        with transaction.atomic():
            deletar_todas_matriculas_da_classe(classe)
            print("Deletadas as matrículas da classe")
            print("Objetos para criar:", len(objetos))

            Matricula.objects.bulk_create(objetos)
            print("bulk_create realizado")
    except IntegrityError as e:
        print(e)
        return {
            "status": "erro",
            "mensagem": "Erro de integridade (registro duplicado)"
        }

    return {
        "status": "ok",
        "importados": len(objetos)
    }
