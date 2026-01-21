from django import forms

from rh.models.cargo import Cargos


class formularioCargo(forms.ModelForm):

    class Meta:
        model = Cargos
        fields=['cargo']
        widgets={
            'cargo': forms.TextInput(attrs={'class':'form-control'})
        }
        
        labels={
            'cargo': 'Cargo'
        }