from django.db import models
from appAno.models import Ano

# Create your models here.
#Classe do ano (NÃO IMPLEMENTADO)
class Classe(models.Model):
    
    class Meta:
        unique_together =(("serie", "turma", "ano"))
        
    PERIODO_CHOICES = (
        ("M","MANHÃ"),
        ("T","TARDE"),
        ("I","INTEGRAL")
    )
    serie = models.CharField(max_length=1, blank=False, null=False )
    turma = models.CharField(max_length=1, blank=False, null=False)
    ano = models.ForeignKey(Ano, on_delete=models.RESTRICT, blank=False, null=False)
    periodo = models.CharField(max_length=1, choices=PERIODO_CHOICES, blank=False, null=False)
    
    def __str__(self):
        periodo = self.retornarDescricaoPeriodo()
        return f'{self.serie}º {self.turma} {periodo}'
    
    def retornarPeriodos():
        return Classe.PERIODO_CHOICES
    
    #Verificar matrículas na sala e retornar o próximo elmento
    def retornarProximoNumeroClasse(tipo_objeto, campo_pesquisa):
        elementos = tipo_objeto.objects.filter(classe=campo_pesquisa)
        numero = len(elementos) + 1
        return numero
    
    def retornarDescricaoPeriodo(self):
        for i in range(len(self.PERIODO_CHOICES)):
            if self.periodo == self.PERIODO_CHOICES[i][0]:
                return self.PERIODO_CHOICES[i][1]
    