from django.db import models

# Create your models here.
class ColetaMetricasBancoSQL(models.Model):
   data_hora = models.DateTimeField(auto_now_add=True)
   operacao = models.CharField(max_length=100)
   sql = models.TextField()
   tempo_execucao_ms = models.FloatField()
   banco = models.CharField(max_length=100, null=True, blank=True)
   endpoint = models.CharField(max_length=200, null=True, blank=True)
   metodo = models.CharField(max_length=10, null=True, blank=True)
   sucesso = models.BooleanField(default=True)
   
   class Meta:
       indexes = [
              models.Index(fields=['data_hora']),
              models.Index(fields=['operacao']),
         ]

    
    
           
               