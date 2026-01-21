from django import forms
from django.forms import SelectMultiple
from django.utils.timezone import now

from rh.models.cargo import Cargos
from rh.models.registro_falta import RegistroFalta
from rh.models.falta import Faltas

# formulário lançamento de faltas
class FormularioLF(forms.ModelForm):

    class Meta:
        model = RegistroFalta
        fields = ['data', 'falta', 'qtd_dias']

        labels = {
            'data': 'Data da Falta',
            'falta': 'Tipo de Falta',
            'qtd_dias': 'Qtde de Dias',
        }

        widgets = {
            'pessoa': forms.HiddenInput(),

            'data': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                },
                format="%Y-%m-%d"
            ),

            'falta': forms.Select(
                attrs={'class': 'form-control'}
            ),

            'qtd_dias': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': 1
                }
            ),
        }



# implementação nova 12/05/2025
class FaltaPesquisaForm(forms.Form):
    data_inicio = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date','class':'form-control'}))
    data_fim = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date', 'class':'form-control'}))
    falta = forms.ModelMultipleChoiceField(
        queryset=Faltas.objects.all().order_by('descricao'),
        required=False,
        widget=SelectMultiple(attrs={'class': 'form-control select2'})
    )

class FaltaPesquisaFormGeral(forms.Form):
    data_inicio = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class':'form-control'}), label='Data Inicial', required=True)
    data_fim = forms.DateField(widget=forms.DateInput(attrs={'type': 'date','class':'form-control'}), label='Data Final', required=True)
    cargo = forms.ModelMultipleChoiceField(
        queryset=Cargos.objects.all().order_by('cargo'),
        required=False,
        widget=SelectMultiple(attrs={'class': 'select2 form-control'}),
        label='Cargo'
    )
    falta = forms.ModelMultipleChoiceField(
        queryset=Faltas.objects.all().order_by('descricao'),
        required=False,
        widget=SelectMultiple(attrs={'class': 'select2 form-control'}),
        label='Tipo de Falta'
    )

    EFETIVO_CHOICES = (
        ('ambos', 'Ambos'),
        ('sim', 'Sim'),
        ('nao', 'Não'),
    )
    efetivo = forms.ChoiceField(choices=EFETIVO_CHOICES, widget=forms.Select(attrs={'class':'form-control'}), required=False, label='Efetivo')

    ATIVO_CHOICES = (
        ('ambos', 'Ambos'),
        ('sim', 'Sim'),
        ('nao', 'Não'),
    )
    ativo = forms.ChoiceField(choices=ATIVO_CHOICES, widget=forms.Select( attrs={'class':'form-control'}), required=False, label='Ativo')


class FiltroRelatorioDescritivoForm(forms.Form):

    SIM_NAO_AMBOS = (
        ('ambos', 'Ambos'),
        ('sim', 'Sim'),
        ('nao', 'Não'),
    )

    SIM_NAO = (
        ('', '---------'),
        ('sim', 'Sim'),
        ('nao', 'Não'),
    )

    data_inicial = forms.DateField(
        label="Data inicial",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    data_final = forms.DateField(
        label="Data final",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    efetivo = forms.ChoiceField(
        label="Efetivo",
        choices=SIM_NAO_AMBOS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    func_publico = forms.ChoiceField(
        label="Funcionário Público",
        choices=SIM_NAO,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

# importação de afastamentos
class ImportarAfastamentosForm(forms.Form):
    arquivo = forms.FileField(
        label="Relatório de afastamentos (PDF)",
        widget=forms.ClearableFileInput(
            attrs={"class": "form-control",
                   "accept": "application/pdf"}
            )                          
    )
