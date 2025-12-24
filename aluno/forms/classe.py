from django import forms
from aluno.models.classe import Classe

class FrmClasse(forms.ModelForm):
    class Meta:
        model = Classe
        fields = ['serie', 'turma', 'periodo']
        widgets = {
            'serie': forms.NumberInput(attrs={
                'class': 'form-control formulario',
                'placeholder': 'Série'
            }),
            'turma': forms.TextInput(attrs={
                'class': 'form-control formulario',
                'placeholder': 'Turma'
            }),
            'periodo': forms.Select(attrs={
                'class': 'form-control formulario'
            }),
        }
        
class FrmClasseUpdate(forms.ModelForm):
    class Meta:
        model = Classe
        fields = ['serie', 'turma', 'periodo']
        widgets = {
            'serie': forms.NumberInput(attrs={
                'class': 'form-control formulario',
                'placeholder': 'Série'
            }),
            'turma': forms.TextInput(attrs={
                'class': 'form-control formulario',
                'placeholder': 'Turma'
            }),
            'periodo': forms.Select(attrs={
                'class': 'form-control formulario'
            }),
        }
