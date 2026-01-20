from rh.models.pessoa import Pessoas

def verificar_ano_saida(pessoa_id):
    pessoa = Pessoas.objects.get(pk=pessoa_id)
   
    ativo = pessoa.saida 
    if ativo is not None:
        ano = pessoa.admissao.year
        if ano >= ativo.year:
            return True
        else:
            return False
    else:
        return True