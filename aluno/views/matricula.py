from datetime import datetime

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

from aluno.models.aluno import Aluno
from aluno.models.ano import Ano
from aluno.models.classe import Classe
from utilitarios.utilitarios import (converter_data_formato_br_str,
                                     criarMensagem, criarMensagemModal)

from aluno.models.matricula import Matricula

from aluno.services.predicao import prever_idade_serie
from aluno.services.matricula import verificar_matricula_ativa, verificar_matricula_ativa_no_ano, deletar_todas_matriculas_da_classe
from aluno.services.matricula import matricular_aluno, movimentar_transferencia, movimentar_remanejamento
# Create your views here.

def matricula(request):
    return render(request, 'aluno/matricula/matricula.html')

def adicionar(reqeust):
    pass

def deletar(request):
    pass

#Buscar aluno
def buscarAluno(request):
    nome = request.GET.get('nome', '')

    alunos = (
        Aluno.objects
        .filter(nome__icontains=nome)
        .order_by('nome')[:5]
    )
    return render(request, 'aluno/matricula/partials/tabela_alunos.html', {
        'alunos': alunos
    })
  
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
   
    return JsonResponse({"serie":classe.serie, 
                         "turma": classe.turma , 
                         "periodo": periodo,
                         "cod_classe": classe.id})

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

def movimentar(request):
    
    try:
        matricula = Matricula.objects.get(pk=request.GET.get('matricula'))
        data_movimentacao = datetime.strptime(request.GET.get('data_movimentacao'),'%Y-%m-%d').date()
        
        STATUS_MOVIMENTACAO = {
            "REMA": movimentar_remanejamento,
            "BXTR": movimentar_transferencia,
        }
           
        if (data_movimentacao > matricula.data_matricula):
            movimentacao = request.GET.get('movimentacao')
            matricula.situacao = movimentacao
            ano = Ano.objects.get(pk=request.GET.get('ano'))
            matricula.ano = ano
            matricula.data_movimentacao = data_movimentacao
            
            return STATUS_MOVIMENTACAO[movimentacao](matricula=matricula, ano=ano, data_movimentacao=data_movimentacao, 
                                                     classe_remanejamento=request.GET.get('classe_remanejamento'))
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


def carregar_linhas_(classe, ordem="numero"):
    linhas = ""
    situacao = ""
    matriculas = Matricula.objects.filter(classe=classe).order_by(ordem)
    numero = 0
    CSS_STATUS = {
        "C": "text-primary",
        "BXTR": "text-danger",
        "TRAN": "text-danger",
        "REMA": "text-success",
        "P": "text-primary",
        "R": "text-danger",
        "NCFP": "text-danger",
    }
    
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


def carregar_linhas(classe, ordem="numero"):
    matriculas = Matricula.objects.filter(classe=classe).order_by(ordem)
    return matriculas

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
    print(matricula.__dict__)
    matricula = {"id_matricula": matricula.id, "rm_aluno": matricula.aluno.rm, "nome_aluno": matricula.aluno.nome, 
                 "data_movimentacao": matricula.data_movimentacao if matricula.data_movimentacao else datetime.now().date() }
  
    return JsonResponse (matricula)





def carregar_matriculas(request):
    classe = request.GET.get('classe')
    matriculas = carregar_linhas(classe)

    if matriculas:
        return render(request, 'aluno/matricula/partials/tabela_matriculas.html', {
            'matriculas': matriculas,
        })
    else:
        return criarMensagem("Sem alunos matriculados", "info")

    
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
   
            rm = Aluno.objects.filter(ra=ra).values('rm').first()

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
