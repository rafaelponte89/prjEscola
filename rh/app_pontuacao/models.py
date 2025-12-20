from django.db import models
from rh.app_pessoa.models import Pessoas

# Create your models here.

class Pontuacoes(models.Model):
    
    ano = models.IntegerField()
    funcao = models.IntegerField()
    cargo = models.IntegerField()
    ue = models.IntegerField()

    pessoa = models.ForeignKey(Pessoas, on_delete=models.CASCADE)
    _use_pessoas_db = True


    class Meta:
        unique_together = ('ano','pessoa')

    def __str__(self):
        return self.ano