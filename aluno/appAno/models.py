from django.db import models


# Create your models here.
class Ano (models.Model):
    ano = models.IntegerField(blank=False, null=False, unique=True)
    fechado = models.BooleanField(blank=False, null=False, default=0)

    def __str__(self):
        return f'{self.ano}'
    
    def avancar(self):
        return self.ano + 1
    
    def voltar(self):
        return self.ano - 1
    
    def fechar_abrir(self):
        return not self.ano
    