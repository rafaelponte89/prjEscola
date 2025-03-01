
# Códigos para testar a aplicação e/ou em desenvolvimento
def rodarTeste():
    j = 0
    for i in range(4999):
        aluno = Aluno(j,"NOME "+ str(i) + "SOBRENOME1 "+ str(i) + "SOBRENOME2"+ str(i))
        j += 1
        aluno.save()
