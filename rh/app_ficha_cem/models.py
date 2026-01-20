from django.db import models
from django.utils.timezone import now

from rh.models.cargo import Cargos
from rh.models.falta import Faltas
from rh.models.pessoa import Pessoas

# Create your models here.

# licença nojo 8 dias corridos
# licença paternidade 5 dias úteis
class Faltas_Pessoas(models.Model):
    
    pessoa = models.ForeignKey(Pessoas, on_delete=models.CASCADE)
    data = models.DateField(default=now)
    falta = models.ForeignKey(Faltas, on_delete=models.CASCADE)
    qtd_dias = models.IntegerField(default=1)
    

    class Meta:
        unique_together=('pessoa','data')

    def __str__(self):
        return f'{self.pessoa}, {self.falta.tipo}, {self.data}'


# 20/05/2025 Salvar Filtros
class FiltroSalvo(models.Model):
    nome = models.CharField(max_length=100)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    efetivo = models.CharField(max_length=10, choices=(('ambos', 'Ambos'), ('sim', 'Sim'), ('nao', 'Não')))
    ativo = models.CharField(max_length=10, choices=(('ambos', 'Ambos'), ('sim', 'Sim'), ('nao', 'Não')))
    cargos = models.ManyToManyField(Cargos, blank=True)
    faltas = models.ManyToManyField(Faltas, blank=True)

    def __str__(self):
        return self.nome
   