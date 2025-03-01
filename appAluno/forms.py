from django import forms
from .models import Aluno

class frmAluno(forms.ModelForm):
    nome = forms.CharField(max_length=100, required=True)
    ra = forms.CharField(max_length=20, required=True,widget=forms.NumberInput)

    nome.widget.attrs["class"] = "form-control formulario"
    nome.widget.attrs["placeholder"] = "Nome do Aluno"
    nome.widget.attrs["aria-describedby"]="basic-addon1"
    ra.widget.attrs["class"] = "form-control"
    ra.widget.attrs["placeholder"] = "RA"
    ra.widget.attrs["class"] = "form-control formulario"
    
    
    def __str__(self):
        return self.nome
    
    class Meta:
        model = Aluno
        fields = ['nome','ra']