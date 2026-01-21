from django.db import models
from datetime import date
from rh.models.cargo import Cargos
from django.contrib.auth.models import User


# Create your models here.
class Pessoas(models.Model):
    EFETIVO =  (
     (True,'Sim'),
     (False,'Não')
    )

    ATIVO = (
        (True,'Sim'),
        (False,'Não')
    )

    PUBLICO = (
        (True, 'Sim'),
        (False, 'Não')
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    id = models.CharField(max_length=6, primary_key=True)
    nome = models.CharField(max_length=150)
    dt_nasc = models.DateField(default=date(1991,1,1))
    cpf = models.CharField(max_length=11, default='11111111111')
    admissao = models.DateField(default=date(1991,1,1))
    saida = models.DateField(null=True, blank=True)
    efetivo = models.BooleanField(choices=EFETIVO, default=False)
    cargo = models.ForeignKey(Cargos, on_delete=models.CASCADE, related_name="pessoas_cargos")
    ativo = models.BooleanField(choices=ATIVO, default=True)
    func_publico = models.BooleanField(choices=PUBLICO, default=True, blank=True)
   
