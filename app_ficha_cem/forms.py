from django import forms
from .models import Pessoas, Faltas_Pessoas, Pontuacoes, Cargos
from bootstrap_datepicker_plus.widgets import DatePickerInput
from django.utils.timezone import now
from .models import Pessoas, Faltas


# formulário lançamento de faltas
class formularioLF(forms.ModelForm):
  
    pessoa = forms.ModelChoiceField(queryset=Pessoas.objects.all(),
                                      widget=forms.HiddenInput())
    data =  forms.DateField(initial=now,
    widget= DatePickerInput()
                                   )
    
    qtd_dias = forms.IntegerField()


    class Meta:
        model = Faltas_Pessoas
        fields = ['data','falta','pessoa','qtd_dias']
        widgets = {
            'data': DatePickerInput()
        }

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


# implementação nova 08/05/2025
class FaltaPesquisaForm(forms.Form):
    data_inicio = forms.DateField(
        label="Data Inicial", widget=forms.DateInput(attrs={'type': 'date'}))
    data_fim = forms.DateField(
        label="Data Final", widget=forms.DateInput(attrs={'type': 'date'}))
    falta = forms.ModelChoiceField(
        label="Tipo de Falta", queryset=Faltas.objects.all(),
        required=False, empty_label="Todos os Tipos"
    )