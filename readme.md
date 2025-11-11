
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
- **Geração Automática das Turmas por ano e período**
- ✅ Matrículas de Alunos
- **Possibilidade de fazer upload de um arquivo da Secretaria Escolar Digital para efetuar todas de uma vez**
- ✅ Baixas de Alunos
- ✅ Remanejamento entre Turmas
- ✅ Relatório de Listas Telefônicas
- ✅ Relatório de Registro de Matrículas
- ✅ Geração de Declaração de Matrícula
- ✅ Lista Personalizada de Assinatura


### 👨‍🏫 Módulo Colaboradores

- ✅ Cadastro de Funcionários
- ✅ Lançamento de Faltas
- ✅ Relatórios de Faltas
- **Ficha de Frequência e Requerimento de Abono Anual Único**
- ✅ Filtros de Faltas


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

### 🔹 Passos

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
pip install -r requirements.txt

# Criar pasta onde serão armazenados os bancos de dados
mkdir bd 

# Criar os bancos de dados
python manage.py migrate --database default
python manage.py migrate --database colaboradores


# Executar o projeto
python manage.py runserver
