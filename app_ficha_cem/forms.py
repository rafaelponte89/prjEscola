from bootstrap_datepicker_plus.widgets import DatePickerInput
from django import forms
from django.forms import SelectMultiple
from django.utils.timezone import now

from .models import Cargos, Faltas, Faltas_Pessoas, Pessoas, Pontuacoes


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


# implementação nova 12/05/2025
class FaltaPesquisaForm(forms.Form):
    data_inicio = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    data_fim = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    falta = forms.ModelMultipleChoiceField(
        queryset=Faltas.objects.all().order_by('descricao'),
        required=False,
        widget=SelectMultiple(attrs={'class': 'select2 form-control'})
    )



class FaltaPesquisaFormGeral(forms.Form):
    data_inicio = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    data_fim = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    cargo = forms.ModelMultipleChoiceField(
        queryset=Cargos.objects.all().order_by('cargo'),
        required=False,
        widget=SelectMultiple(attrs={'class': 'select2 form-control'})
    )
    falta = forms.ModelMultipleChoiceField(
        queryset=Faltas.objects.all().order_by('descricao'),
        required=False,
        widget=SelectMultiple(attrs={'class': 'select2 form-control'})
    )

    EFETIVO_CHOICES = (
        ('ambos', 'Ambos'),
        ('sim', 'Sim'),
        ('nao', 'Não'),
    )
    efetivo = forms.ChoiceField(choices=EFETIVO_CHOICES, required=False)

    ATIVO_CHOICES = (
        ('ambos', 'Ambos'),
        ('sim', 'Sim'),
        ('nao', 'Não'),
    )
    ativo = forms.ChoiceField(choices=ATIVO_CHOICES, required=False)


class FiltroRelatorioDescritivoForm(forms.Form):
    EFETIVO_CHOICES = (
        ('ambos', 'Ambos'),
        ('sim', 'Sim'),
        ('nao', 'Não'),
    )
    ATIVO_CHOICES = (
        ('sim', 'Sim'),
        ('nao', 'Não'),
    )

    PUBLICO_CHOICES = (
        ('sim', 'Sim'),
        ('nao', 'Não'),
    )

    data_inicial = forms.DateField(label="Data inicial", widget=forms.DateInput(attrs={'type': 'date'}))
    data_final = forms.DateField(label="Data final", widget=forms.DateInput(attrs={'type': 'date'}))
    efetivo = forms.ChoiceField(choices=EFETIVO_CHOICES, required=False)
    
    ativo = forms.ChoiceField(choices=ATIVO_CHOICES, required=False)
    func_publico =  forms.ChoiceField(choices=PUBLICO_CHOICES, required=False, label="Funcionário Público")


# importação de afastamentos
class ImportarAfastamentosForm(forms.Form):
    arquivo = forms.FileField(
        label="Relatório de afastamentos (PDF)",
        widget=forms.ClearableFileInput(
            attrs={"class": "form-control",
                   "accept": "application/pdf"}
            )                          
    )
