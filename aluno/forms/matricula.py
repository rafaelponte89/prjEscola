from django import forms
# importação de afastamentos
class ImportarMatriculasForm(forms.Form):
    arquivo = forms.FileField(
        label="Relatório de Matrícula da Classe (PDF)",
        widget=forms.ClearableFileInput(
            attrs={"class": "form-control",
                   "accept": "application/pdf"}
            )                          
    )