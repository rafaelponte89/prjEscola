from django import forms
from rh.models.pessoa import Pessoas


class FormularioPessoa(forms.ModelForm):

    class Meta:
        model = Pessoas
        fields = [
            'id','nome','dt_nasc','cpf',
            'admissao','saida','efetivo',
            'cargo','ativo','func_publico'
        ]
        widgets = {
            'id': forms.TextInput(attrs={'class':'form-control disable'}),

            'nome': forms.TextInput(attrs={'class':'form-control'}),
            'cargo': forms.Select(attrs={'class':'form-control'}),
            'efetivo': forms.Select(attrs={'class':'form-control'}),
            'ativo': forms.Select(attrs={'class':'form-control'}),
            'func_publico': forms.Select(attrs={'class':'form-control'}),

            'cpf': forms.TextInput(attrs={'class':'form-control'}),
            'dt_nasc': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'},
                format='%Y-%m-%d'
            ),
            'admissao': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'},
                format='%Y-%m-%d'
            ),
            'saida': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'},
                format='%Y-%m-%d'
            ),
        }
        
        labels= {
            'func_publico': 'Func. Pub.',
            'dt_nasc': 'Data de Nascimento',
            'admissao': 'Data de Admissão',
            'saida': 'Data de Saída',
            'id': 'Matrícula',
            'cpf':'CPF'
        }

    def __init__(self, *args, **kwargs):
        super(FormularioPessoa, self).__init__(*args, **kwargs)
        
        # Verifica se o formulário está sendo carregado com uma instância (ex: para atualização)
        if 'instance' in kwargs and kwargs['instance'] is not None:
            self.fields['id'].widget.attrs['readonly'] = True  # Torna o campo 'id' somente leitura
            self.fields['id'].required = False  # Torna o campo não obrigatório