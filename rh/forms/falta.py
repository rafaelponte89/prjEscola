from django import forms

from rh.models.falta import Faltas


# formulário tipo de faltas
class formularioTF(forms.ModelForm):

    tipo = forms.CharField(max_length=3, required=True)
    descricao = forms.CharField(max_length=30, required=True)

    class Meta:
        model = Faltas
        fields = ['tipo','descricao']