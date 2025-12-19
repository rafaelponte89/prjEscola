# insere a chave dentro da lista 16/04/2025
def inserir_chave(dicionario, chave):
    for k,v in dicionario[chave].items():
        v.insert(0,k)


def transformar_em_um_dicionario(funcao,cargo,ue):
    
    meses_pontuacao = {}
    cargo_lst = []
    funcao_lst = []
    ue_lst = []
    for v in cargo.values():
        cargo_lst.append(v)
    
    for v in funcao.values():
        funcao_lst.append(v)

    for v in ue.values():
        ue_lst.append(v)

    i = 0
    for k, v in cargo.items():
        meses_pontuacao[k] = [funcao_lst[i],cargo_lst[i], ue_lst[i]]
        i = i + 1

    return meses_pontuacao


def formatar_cargo_disciplina(pessoa):

    cargo = str(pessoa.cargo)
    if '-' in cargo:
        cargo_disciplina = tuple(cargo.split('-'))
    else:
        cargo_disciplina = cargo + '-N/A'
        cargo_disciplina = tuple(cargo_disciplina.split('-'))

    return cargo_disciplina