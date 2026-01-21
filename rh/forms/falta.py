from django import forms

from rh.models.falta import Faltas


# formulário tipo de faltas
class formularioTF(forms.ModelForm):

    

    class Meta:
        model = Faltas
        fields = ['tipo','descricao']
        
        widgets={
            'tipo':forms.TextInput(attrs={'class':'form-control'},),
            'descricao': forms.TextInput(attrs={'class':'form-control'})
        }
        
        labels = {
            'tipo':'Sigla',
            'descricao': 'Descrição'
        }