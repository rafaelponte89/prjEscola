
# 📘 Projeto Escola

> O **Projeto Escola** é um sistema de gestão escolar desenvolvido em **Python/Django**, criado com o objetivo de modernizar e automatizar as rotinas administrativas e pedagógicas das escolas públicas municipais.  
> O sistema foi concebido durante o **Curso de Engenharia** e evoluiu para um ambiente funcional e em produção, sendo atualmente utilizado pela **EMEB Profª Victória Olivito Nonino**, localizada em **Orlândia/SP**.  

Com foco em **eficiência, organização e acessibilidade**, o Projeto Escola permite o gerenciamento completo de **alunos, turmas e colaboradores**, simplificando atividades que antes dependiam de processos manuais e demorados.  
Entre suas principais funcionalidades estão o **cadastro e remanejamento de alunos**, **geração automática de turmas**, **emissão de relatórios oficiais**, **controle de faltas de colaboradores** e **exportação de declarações personalizadas**.

O sistema foi projetado para funcionar em **rede local**, hospedado em um **servidor IIS (Internet Information Services)** rodando em **Windows 7**, sendo acessado pelos computadores da instituição através do **endereço IP e porta configurados**.  
Essa arquitetura permite que diferentes setores da escola — como secretaria, direção e coordenação — acessem e atualizem as informações de forma centralizada e segura, mesmo em ambientes sem acesso à internet.

Mais do que um simples cadastro, o Projeto Escola visa proporcionar **integração entre dados administrativos e pedagógicos**, reduzindo erros humanos, otimizando o tempo da equipe e oferecendo **relatórios automatizados** que facilitam a gestão escolar e o acompanhamento do desempenho institucional.

---

## 🚀 Funcionalidades Principais

### 👩‍🎓 Módulo Alunos

- ✅ Cadastro de Alunos
- ✅ Cadastro de Turmas
- ✅ Geração Automática das Turmas por ano e período
- ✅ Matrículas de Alunos
- ✅ Possibilidade de fazer upload de um arquivo da Secretaria Escolar Digital para efetuar todas de uma vez
- ✅ Baixas de Alunos
- ✅ Remanejamento entre Turmas
- ✅ Relatório de Listas Telefônicas
- ✅ Registro de Matrículas por Turma
- ✅ Geração de Declaração de Matrícula
- ✅ Lista Personalizada de Assinatura


### 👨‍🏫 Módulo Colaboradores

- ✅ Cadastro de Funcionários
- ✅ Lançamento de Faltas
- ✅ Relatórios de Faltas
- ✅ Ficha de Frequência e Requerimento de Abono Anual Único
- ✅ Filtros de Faltas
- ✅ Requerimento de Falta Abonada
- ✅ Importação de afastamentos de relatório pdf




---

## 🧠 Tecnologias Utilizadas

- **Linguagem:** Python / JavaScript.
- **Framework:** Django.
- **Banco de Dados:** SQLite 
- **Outras:** Bootstrap.

---

## ⚙️ Instalação e Execução

### 🔹 Pré-requisitos

- Python 3.12.
- Git instalado

### 🔹 Passos Execução na Máquina (Baremetal)

```bash
# Clonar o repositório
git clone https://github.com/rafaelponte89/prjEscola.git

# Entrar na pasta do projeto
cd prjEscola

# Criar e ativar ambiente virtual (Python)
python -m venv env
source env/bin/activate  # Linux/Mac
env\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt --no-cache-dir

# Criar pasta onde serão armazenados os bancos de dados
mkdir bd 

# Criar os bancos de dados
python manage.py migrate --database=aluno 
python manage.py migrate --database=rh 
python manage.py migrate --database=default 
python manage.py migrate 
python manage.py collectstatic --noinput 
python manage.py create_super_central 

# Executar o projeto
python manage.py runserver

### 🔹 Passos - Container Docker

```bash
# Instalar docker conforme sistema operacional e executar
https://docs.docker.com/desktop/?_gl=1*18ru53h*_gcl_au*MTA4Mjc0NTAxMy4xNzcxNzg5Nzk2*_ga*MTg1NjkwNDA0OS4xNzcxNzg5Nzk3*_ga_XJWPQMJYHQ*czE3NzE3ODk3OTYkbzEkZzEkdDE3NzE3ODk3OTckajU5JGwwJGgw

# Criar a pasta sistema_escolar no disco C:\ caso seja em outro o arquivo de configuração docker-compose.yml deverá ser modificado 
mkdir sistema_escolar

# Entrar na pasta sisema_escolar
cd sistema_escolar

# Clonar o repositório
git clone https://github.com/rafaelponte89/prjEscola.git

# Entrar na pasta prjEscola
cd prjEscola

# Verificar se os caminhos no arquivo de configuração do docker-compose se aplicam ao seu caminnho (
# Se o disco for representado por outra letra o arquivo de configuração deve ser modificado
C:/sistema_escolar/prjEscola-main

# Caso fosse D teria que mudar para o caminho abaixo todo o arquivo de configuração docker-compose.yml
D:/sistema_escolar/prjEscola-main

# Usar o comando para subir os containers
docker-compose up -d

# Acesso
No navegador colocar:
http://localhost/

# Comando para remover os containers
docker-compose down






