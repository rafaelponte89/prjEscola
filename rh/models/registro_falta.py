from django.db import models
from django.utils.timezone import now
from rh.models.pessoa import Pessoas
from rh.models.falta import Faltas

class RegistroFalta(models.Model):
    pessoa = models.ForeignKey(Pessoas, on_delete=models.CASCADE)
    data = models.DateField(default=now)
    falta = models.ForeignKey(Faltas, on_delete=models.CASCADE)
    qtd_dias = models.IntegerField(default=1)
    

    class Meta:
        unique_together=('pessoa','data')
        db_table = "rh_faltas_pessoas"

    def __str__(self):
        return f'{self.pessoa}, {self.falta.tipo}, {self.data}'
