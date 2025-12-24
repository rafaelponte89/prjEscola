from django import forms
from aluno.models.aluno import Aluno
from aluno.utils.texto import padronizar_nome

class FrmAluno(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = ['nome', 'ra']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control formulario',
                'placeholder': 'Nome do Aluno',
                'aria-describedby': 'basic-addon1'
            }),
            'ra': forms.NumberInput(attrs={
                'class': 'form-control formulario',
                'placeholder': 'RA'
            }),
        }
        
    def clean_nome(self):
        nome = self.cleaned_data.get('nome')
        return padronizar_nome(nome)

class FrmAlunoUpdate(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = [
            'nome',
            'ra',
            'd_ra',
            'data_nascimento',
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'ra': forms.NumberInput(attrs={'class': 'form-control'}),
            'd_ra': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': 1
            }),
            'data_nascimento': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),
        }

    def clean_nome(self):
        nome = self.cleaned_data.get('nome')
        return padronizar_nome(nome)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_nascimento'].input_formats = ['%Y-%m-%d']


        
        

    