from django import forms
from django.forms.widgets import SelectDateWidget
from app_cargo.models import Cargos
from .models import Pessoas
from django.utils.timezone import now
from datetime import date
from bootstrap_datepicker_plus.widgets import DatePickerInput

class formularioPessoa(forms.ModelForm):
    cargos = Cargos.objects.all()



    id = forms.CharField(max_length=6, required=True)

    nome = forms.CharField(max_length=150, required=True)

        
    dt_nasc =  forms.DateField(widget=DatePickerInput(), label="Data de Nascimento")

    cpf = forms.CharField(max_length=11, required=True, label='CPF')
    efetivo = forms.ChoiceField(choices=Pessoas.EFETIVO,widget= forms.RadioSelect)
    cargo = forms.ModelChoiceField(queryset=cargos)
   
    admissao =  forms.DateField(widget=DatePickerInput(), label="Data de Admissão")

    saida = forms.DateField(widget=DatePickerInput(), label="Data de Saída", required=False)

    ativo = forms.ChoiceField(choices=Pessoas.ATIVO, widget= forms.RadioSelect)


    class Meta:
        model = Pessoas
        fields = ['id','nome','dt_nasc','cpf','admissao','saida','efetivo','cargo','ativo']
        widget = {
            "dt_nasc": DatePickerInput(),
            "admissao": DatePickerInput(),
            "saida": DatePickerInput()
           
        }
        
    def __init__(self, *args, **kwargs):
        super(formularioPessoa, self).__init__(*args, **kwargs)
        
        # Verifica se o formulário está sendo carregado com uma instância (ex: para atualização)
        if 'instance' in kwargs and kwargs['instance'] is not None:
            self.fields['id'].widget.attrs['readonly'] = True  # Torna o campo 'id' somente leitura
            self.fields['id'].required = False  # Torna o campo não obrigatório