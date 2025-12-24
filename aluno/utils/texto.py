def padronizar_nome(nome):
    acentuados = {'Á':'A','Ã':'A','Â':'A','É':'E','Ê':'E','Í':'I','Î':'I','Ó':'O','Õ':'O','Ô':'O','Ú':'U','Û':'U','Ç':'C','\'':'','`':''}   
    #acentuados = {'Á':'A','Ã':'A','Â':'A','É':'E','Ê':'E','Í':'I','Î':'I','Ó':'O','Õ':'O','Ô':'O','Ú':'U','Û':'U'} 
    if nome is not None:  
        nome = nome.upper().strip()
        letra_nova = ''
        for letra in nome:
            if letra in acentuados.keys():
                letra_nova = acentuados[letra]
                nome = nome.replace(letra, letra_nova)
            
        return nome.rstrip(' ').lstrip(' ')
    