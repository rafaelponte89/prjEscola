from datetime import datetime

from django.db.models import Q
from django.shortcuts import HttpResponse, render

from aluno.models.aluno import Aluno
from aluno.models.ano import Ano
from aluno.models.classe import Classe
from utilitarios.utilitarios import (converter_data_formato_br_str,
                                     criarMensagem, criarMensagemModal)

from aluno.models.matricula import Matricula

# Create your views here.

def matricula(request):
    
    return render(request, 'aluno/matricula/matricula.html')


def adicionar(reqeust):
    pass


def deletar(request):
    pass


#Buscar aluno
def buscarAluno(request):
    nome = request.GET.get('nome')   
    # Se status não ativo
    alunos = Aluno.objects.filter(Q(nome__contains=nome))[:5]
    linhas = ''
    for a in alunos:
        linhas += f"""<tr><td>{a.nome}</td><td>{a.ra}</td><td class='text-center'><button type="button" class="btn btn-outline-dark btn-lg adicionarNaClasse"
                        value={a.rm} > 
                        <i class="bi bi-plus-circle-fill"></i>
                        </button></td></tr>"""
    
    return HttpResponse(linhas)    




def calcular_idade(data_nascimento, data_referencia):
    # Calcule a diferença de anos
    idade = data_referencia.year - data_nascimento.year

    # Ajuste se o aniversário ainda não tiver ocorrido naquele ano
    if (data_referencia.month, data_referencia.day) < (data_nascimento.month, data_nascimento.day):
        idade -= 1

    return idade

def prever_idade_serie(aluno):
    import joblib
    import pandas as pd

    # carregar modelo
    modelo = joblib.load('modelos_ml/modelo_tree_classifier_v1.pkl')

    data_nascimento = datetime.strptime(aluno.data_nascimento,'%Y-%m-%d')
    data_base = datetime.strptime(f'{datetime.now().year}-03-31','%Y-%m-%d')
   
    idade = calcular_idade(data_nascimento, data_base)
    
    # Preparar novo dado de entrada
    novo_objeto = pd.DataFrame({'idade': [idade]})
    predicao = modelo.predict(novo_objeto)
 
    return predicao

def matricular_aluno_ia(request):
    aluno = Aluno.objects.get(pk=request.POST.get('aluno'))
    ano = Ano.objects.get(pk=request.POST.get('ano'))
    previsao = prever_idade_serie(aluno)[0]
    classes = Classe.objects.filter(ano=ano).filter(serie=previsao)
    print(classes)
    menor = 99
    classe_sel=''
    for classe in classes:
        matriculas = Matricula.objects.filter(classe=classe)
        if(len(matriculas)) <= menor:
            menor = len(matriculas)
            classe_sel= classe
  
    try:
       
        resposta =  matricular_aluno(ano=ano, aluno=aluno,classe=classe_sel, numero=Classe.retornarProximoNumeroClasse(Matricula, classe_sel),
                     data_matricula=datetime.now(), m_sucesso=f'Matriculado com sucesso! Na Classe {classe} - Ano: {ano}')
            
        return resposta
    except Exception as err:
        return criarMensagem(f'Não existe {previsao}º ano para matricular o aluno!','danger')
    
#Exibir tela da matrícula  
def exibirTelaMatricula(request):
    codigo_classe = request.GET.get("classe")
    classe = Classe.objects.get(pk=codigo_classe)
    
    periodo = Classe.retornarDescricaoPeriodo(classe)
            
    tela = f"""<form>
                    <h5 class='bg-body-secondary d-flex rounded-5 justify-content-center p-2'><strong>{classe.serie}º{classe.turma} - {periodo} </strong></h5>
                    <input type='hidden' id='codClasseMatricula' value={classe.id} />
                    <div class='row'>
                    <div class='col form-group'>
                    <label for='pesquisaAluno'>Nome</label>
                    <input id='pesquisaAluno' class='form-control' type='text'/>
                    </div>   
                    <div class='col-5 form-group'> 
                    <label for='dataMatriculaIndividual'>Data da Matrícula</label>
                    <input id='dataMatriculaIndividual' class='form-control' type='date' value='{datetime.now().strftime("%Y-%m-%d")}'/>
                    </div>               
                    </div>
                    <div class='row'>
                    
                    </div>
                    
                    </form>"""
   
    return HttpResponse(tela)

    
#Adicionar aluno na classe        
def adicionarNaClasse(request):
    try:
         
        aluno = Aluno.objects.get(pk=request.GET.get('aluno'))
        ano = request.GET.get('ano')
        ano = Ano.objects.get(pk=ano)
        
        classe = Classe.objects.get(pk=request.GET.get('classe'))
           
        resposta = matricular_aluno(ano, classe, aluno, 
                              Classe.retornarProximoNumeroClasse(Matricula, classe),
                              request.GET.get('data_matricula'))
            
        return resposta
        

    except Exception as error:    
        print(error)
        return criarMensagemModal(f"Erro ao efetuar a Matrícula", "danger")


def matricular_aluno(ano, classe, aluno, numero, data_matricula, data_movimentacao=None, situacao='C', m_sucesso='Matriculado com Sucesso!!!', m_tipo='M'):
   
    if ano.fechado:
        return criarMensagemModal(f'Ano {ano} fechado!','danger')
    else:
        if (verificar_matricula_ativa_no_ano(ano=ano, rm=aluno)):
            matricula = Matricula.objects.filter(aluno=aluno)

            # Se aluno matriculado na mesma serie o status de promovido é alterado para reprovado e salvo
            for m in matricula:
                if m.classe.serie == classe.serie:
                    if m.situacao == 'P':
                        m.situacao = 'R'
                        m.save()

            matricula_nova = Matricula(ano=ano, classe=classe, aluno=aluno, 
                                    numero=numero,
                                    data_matricula=data_matricula, 
                                    data_movimentacao=data_movimentacao,
                                    situacao=situacao,
                                    )

            matricula_nova.save()
            aluno.status = 2
            aluno.save()
            if m_tipo != 'M':
                return criarMensagemModal(m_sucesso,'success')
            else:
                return criarMensagem(m_sucesso,'success')
        else:
            return criarMensagemModal('Aluno com Matricula Ativa!','danger')



def movimentar(request):
    
    try:
       
        matricula = Matricula.objects.get(pk=request.GET.get('matricula'))
        data_movimentacao = datetime.strptime(request.GET.get('data_movimentacao'),'%Y-%m-%d').date()
       
    
        if (data_movimentacao > matricula.data_matricula):
            movimentacao = request.GET.getlist('movimentacao')[0]
            matricula.situacao = movimentacao
            ano = Ano.objects.get(pk=request.GET.get('ano'))
            matricula.ano = ano
            matricula.data_movimentacao = data_movimentacao
            
            if(movimentacao == "REMA"):
                matricula.save()
                
                classe = (Classe.objects.get(pk=request.GET.getlist('classe_remanejamento')[0]) if (request.GET.getlist('classe_remanejamento')[0]) != '0' else None)
                resposta = matricular_aluno(ano,classe, matricula.aluno,
                                    Classe.retornarProximoNumeroClasse(Matricula, classe),
                                    data_movimentacao, m_sucesso="Remanejamento Efetuado!")
                    
                return resposta
        
            elif (movimentacao == "BXTR"):
                aluno = Aluno.objects.get(pk=matricula.aluno.rm)
                aluno.status = 0
                aluno.save()
                matricula.save()

                return criarMensagem("Transferência efetuada!", "success")
            else:
                return criarMensagem("Movimentação efetuada!", "success")
        else:
            return criarMensagem("Data da movimentação deve ser maior que a data da matrícula!", "warning")


        
    except Exception as erro:
        print(erro)
        return criarMensagem(f"Erro ao efetuar o Remanejamento!{erro}",
                             "danger")
        


def ordernar_alfabetica(request):
    classe = request.GET.getlist('classe')[0]
    linhas = carregar_linhas(classe, 'aluno__nome')
    return HttpResponse(linhas)


def carregar_movimentacao(request):
   
    movimentacoes = Matricula.retornarSituacao()
    opcoes = "<option value='0'>Selecione</option>"
                                            
    for m in movimentacoes:
     
        if m[0] == "BXTR":
            situacao = "TRANSFERIDO"
        elif m[0] == "REMA":
            situacao = "REMANEJADO"
        elif m[0] == "NCFP":
            situacao = "Ñ COMP. FORA PRAZO"
            
        if m[0] not in ['C','P','R']:
            opcoes += f"<option value={m[0]}>{situacao} </option>"
        
    return HttpResponse(opcoes)


def carregar_classes_remanejamento(request):
    ano = request.GET.get('ano')
    ano = Ano.objects.get(pk=ano)
     
    classe_atual = Classe.objects.get(pk=request.GET.get('serie'))
    classes = Classe.objects.filter(ano=ano, serie=classe_atual.serie)
    classes = classes.exclude(pk=request.GET.get('serie'))
    opcoes = "<option value='0'>Selecione</option>"
                                            
    for c in classes:
       periodo = Classe.retornarDescricaoPeriodo(c)
       opcoes += f"<option value={c.id}>{c.serie}º {c.turma} - {periodo}</option>"
        
    return HttpResponse(opcoes)


#def carregar_classes(request):
 
#    ano = request.GET.get('ano')
#    classes = Classe.objects.filter(ano=ano)
#    opcoes = "<option value='0'>Selecione</option>"
                                            
#    for c in classes:
#        periodo = Classe.retornarDescricaoPeriodo(c)
#        opcoes += f"<option value={c.id}>{c.serie}º {c.turma} - {periodo}</option>"
        
#    return HttpResponse(opcoes)  


def carregar_linhas(classe, ordem="numero"):
    linhas = ""
    situacao = ""
    matriculas = Matricula.objects.filter(classe=classe).order_by(ordem)
    numero = 0
    
    if ordem == "aluno__nome":
        for m in matriculas:
            numero = numero + 1
            m.numero = numero
            m.save()
    cor = "text-dark"        
    for m in matriculas:
        situacao = Matricula.retornarDescricaoSituacao(m)

        if m.situacao == "C":
            cor = "text-primary"
        elif m.situacao == "BXTR" or m.situacao == "TRAN":
            cor = "text-danger"
        elif m.situacao == "REMA":
            cor = "text-success"
        elif m.situacao == "P":
            situacao = "PROMOVIDO"
            cor = "text-primary"
        elif m.situacao == "R":
            situacao = "REPROVADO"
            cor = "text-danger"
        elif m.situacao == "NCFP":
            cor = "text-danger"
            situacao = "Ñ COMP. FORA PRAZO"
        else:
            situacao = "INDEFINIDA"
        if m.data_movimentacao is None:
            m.data_movimentacao = ''
            
        linhas += f"""<tr> <td class='text-center'><button class='rounded-circle bg-light text-dark border-success'>{m.numero} </button></td> <td >{m.aluno.nome}</td> <td class={cor}> {situacao} </td> 
                            <td  class='text-center'> {m.data_matricula.strftime('%d/%m/%Y')} </td> 
                            <td  class='text-center text-danger'> {converter_data_formato_br_str(m.data_movimentacao)} </td>
                        <td class='text-center'> <button type='button' class='btn btn-outline-dark btn-lg movimentar'
          value={m.id} data-bs-toggle='modal' data-bs-target='#movimentarModal'> 
                           <i class="bi bi-arrow-down-up"></i>
                        </button></td>
                                     <td class='text-center'> <button type='button' class='btn btn-outline-dark btn-lg excluir'
          value={m.id} > 
                          <i class="bi bi-trash3-fill"></i>
                        </button></td></tr>"""
        
    return linhas


def excluir_matricula(request):
  
        matricula = request.GET.get('matricula')
        matricula = Matricula.objects.get(pk=matricula)
        aluno = Aluno.objects.get(pk=matricula.aluno.rm)
        if matricula:
            matricula.delete()
            aluno.status = 0
            aluno.save()
            return criarMensagem("Matrícula excluída com sucesso!", "success")
    
    


def buscar_matricula(request):
    matricula = request.GET.get('matricula')
    matricula = Matricula.objects.get(pk=matricula)
    corpo = ""
    
    corpo = f"""<form>
                    <input type='hidden' id='matricula' value={matricula.id} />
                    <div class='row'>
                    <div class='col form-group'>
                    <label for='rmAluno'>RM</label>
                    <input id='rmAluno' class='form-control' type='text' value='{matricula.aluno.rm}' disabled='disabled'\>
                    </div>
                    </div>
                    
                    <div class='row'>
                    <div class='col form-group'> 
                    <label for='nomeAluno'>Aluno</label>
                    <input id='nomeAluno' class='form-control' type='text' value='{matricula.aluno.nome}' disabled='disabled'\>
                    </div>
                    </div>
                    
                    <div class='row>
                    <div class='col form-group'> 
                    <label for='dataMovimentacao'>Data Movimentação</label>
                    <input id='dataMovimentacao' class='form-control' type='date' value='{matricula.data_movimentacao}' \>
                    </div>     
                    </div> 
                </form>
                """
    
    return HttpResponse(corpo)
    
def carregar_matriculas(request):
    classe = request.GET.get('classe')
    linhas = carregar_linhas(classe, 'numero')  
    if linhas:
        return HttpResponse(linhas)
    else:
        return criarMensagem("Sem alunos matriculados","info")


# Verificar se existe matrícula ativa no ano, se não possuir pode matricular
# Se possuir não pode
def verificar_matricula_ativa_no_ano(ano, rm, situacao='C'):
    matriculas = Matricula.objects.filter(Q(ano=ano) & Q(aluno_id=rm) & Q(situacao=situacao))  
    return False if matriculas else True 

# Verificar se existe matrícula ativa, se não possuir pode matricular
def verificar_matricula_ativa(rm, situacao='C'):
    matriculas = Matricula.objects.filter(Q(aluno_id=rm) & Q(situacao=situacao) )  
    return False if matriculas else True 
  
# Veriricar se aluno já foi matriculado na mesma série  no mesmo ano 09/10/2024       
def verificar_matricula_na_mesma_serie_ano_corrente(matricula,serie):

    for m in matricula:
        print(m.classe.serie)
    return False if matricula else True

# Veriricar se aluno já foi matriculado na mesma série qualquer ano 09/10/2024       
#def verificar_matricula_na_mesma_serie_mesmo_ano(rm, serie):
#    matriculas = Matricula.objects.filter(Q(aluno_id=rm) & Q(serie=serie))
#    return False if matriculas else True


def deletar_todas_matriculas_da_classe(classe):
    matriculas = Matricula.objects.filter(classe=classe)
    matriculas.delete()
    for matricula in matriculas:
        aluno = Aluno.objects.filter(rm=matricula.aluno.rm)
        aluno.status = 0
        aluno.save()
    
    
# EM DESENVOLVIMENTO 26/02/2024
# modulo que efetuará todas as matrículas através de uma arquivo csv do próprio SED
def upload_matriculas(request):
    try:
        matriculas = request.GET.get('matriculas')
        linhas = ((matriculas.encode('utf-8')).decode('utf-8')).split('\n')
        linhas_array = []
        classe = int(request.GET.get('classe'))
        classe = Classe.objects.get(pk=classe)
        ano = request.GET.get('ano')
        ano = Ano.objects.get(pk=ano)
       
        data_matricula = request.GET.get('data_matricula')
        
        deletar_todas_matriculas_da_classe(classe)
        
        for linha in range(3, len(linhas)):
            linhas_array.append(linhas[linha].split(';'))
    
        for linha in range(len(linhas_array)-1):  
            ra = int(linhas_array[linha][4])  
            situacao = ('C' if (len(linhas_array[linha][9]) == 0)
                        else linhas_array[linha][9])
            
            data_movimentacao = (None if(len(linhas_array[linha][10]) == 0) else 
                                 datetime.strptime(linhas_array[linha][10],"%d/%m/%Y"))
            print(data_movimentacao)
   
            rm = Aluno.objects.filter(ra=ra).values('rm')[:1]

            for cod in rm:
                aluno = Aluno.objects.get(pk=cod['rm'])
                
                if (verificar_matricula_ativa(aluno.rm) or data_movimentacao):
                   
                    aluno.status = 2
                    numero = Classe.retornarProximoNumeroClasse(Matricula, classe)
                    print("Situação",situacao)
                    print("Data Movimentacao",data_movimentacao)
                    print("data Matricula", data_matricula)
                    matricula = Matricula(ano=ano, classe=classe, aluno=aluno, 
                                    situacao=situacao, 
                                    data_matricula=data_matricula, numero=numero, data_movimentacao=data_movimentacao)
            
                    matricula.save()
                    aluno.save()                
                
        return HttpResponse(carregar_linhas(classe))
    
    except Exception as e:
        return HttpResponse(carregar_linhas(0))
        
        
    #Visualizar alunos da classe
