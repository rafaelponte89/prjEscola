# Base Python
FROM python:3.12-slim

# Diretório de trabalho dentro do container
WORKDIR /app

# Copia só requirements primeiro (cache do Docker)
COPY requirements.txt .

# Atualiza pip e instala dependências
RUN pip install --upgrade pip \
    && pip install -r requirements.txt 
    

# Copia todo o código
COPY . .

# Porta padrão
EXPOSE 8000

# Comando padrão para iniciar o Django via Waitress
CMD ["waitress-serve", "--listen=*:8000", "prjEscola.wsgi:application"]
