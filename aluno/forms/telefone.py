# forms.py
from django import forms
from aluno.models.telefone import Telefone
from django.forms import inlineformset_factory
from aluno.models.aluno import Aluno

class TelefoneForm(forms.ModelForm):
    class Meta:
        model = Telefone
        fields = ['numero', 'contato']
        widgets = {
            'numero': forms.TextInput(attrs={
                'class': 'form-control numTelefone p-2',
                'placeholder': 'Telefone'
            }),
            'contato': forms.Select(attrs={
                'class': 'form-select m-3 contato'
            }),
        }

TelefoneFormSet = inlineformset_factory(
    Aluno,
    Telefone,
    form=TelefoneForm,
    extra=0,        # não cria telefones vazios
    can_delete=True,

)