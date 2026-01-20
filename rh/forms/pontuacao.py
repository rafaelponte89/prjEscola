from django import forms
from rh.models.pontuacao import Pontuacoes
from rh.models.pessoa import Pessoas

class formularioPontuacao(forms.ModelForm):
    ano = forms.IntegerField(min_value=0)
    funcao = forms.IntegerField(min_value=0)
    cargo = forms.IntegerField(min_value=0)
    
    ue = forms.IntegerField(min_value=0)

    pessoa = forms.ModelChoiceField(queryset=Pessoas.objects.all(),
                                      widget=forms.HiddenInput())

    class Meta:
        model = Pontuacoes
        # fields = ['ano','cargo','funcao','ue','pessoa',]
        fields = ['ano','funcao','cargo','ue','pessoa']