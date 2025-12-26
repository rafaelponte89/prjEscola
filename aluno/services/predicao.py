
from aluno.services.aluno import calcular_idade
from datetime import datetime

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