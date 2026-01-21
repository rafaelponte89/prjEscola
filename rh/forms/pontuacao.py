from django import forms
from rh.models.pontuacao import Pontuacoes
from rh.models.pessoa import Pessoas

class formularioPontuacao(forms.ModelForm):
   

    class Meta:
        model = Pontuacoes
        # fields = ['ano','cargo','funcao','ue','pessoa',]
        fields = ['ano','funcao','cargo','ue','pessoa']
        widgets = {
            'ano': forms.NumberInput(attrs={'class':'form-control','min':0}),
            'funcao': forms.NumberInput(attrs={'class':'form-control','min':0}),
            'ue': forms.NumberInput(attrs={'class':'form-control','min':0}),
            'cargo': forms.NumberInput(attrs={'class':'form-control','min':0}),

            'pessoa': forms.HiddenInput()
        }
        labels = {
            'ano': 'Ano',
            'ue': 'Unidade Escolar',
            'cargo': 'Cargo',
            'funcao': 'Função'
        }