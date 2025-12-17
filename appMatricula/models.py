from django.db import models

from appAluno.models import Aluno
from appAno.models import Ano
from appClasse.models import Classe


# Create your models here.
#Matrícula do aluno (NÃO IMPLEMENTADO)
class Matricula(models.Model):
    SITUACAO = (
        ('C', 'CURSANDO'),
        ('BXTR', 'TRANSFERIDO'),
        ('REMA', 'REMANEJADO'),
        ('NCFP', 'Ñ COMP. FORA PRAZO'),
        ('P', 'PROMOVIDO'),
        ('R', 'REPROVADO'),
    )
    ano = models.ForeignKey(Ano, on_delete=models.RESTRICT, blank=False, null=False, default=0)
    classe = models.ForeignKey(Classe, on_delete=models.RESTRICT, default='')
    aluno = models.ForeignKey(Aluno, on_delete=models.RESTRICT, default='')
    numero = models.IntegerField(blank=False, null=False, default=0)
    situacao = models.CharField(max_length=4, choices=SITUACAO, default='A')
    data_matricula = models.DateField(null=True)
    data_movimentacao = models.DateField(null=True)
    
    def __str__(self):
        return f'{self.aluno} - {self.classe}' 
    
    class Meta:
        unique_together = ['ano', 'aluno', 'situacao', 'data_matricula','data_movimentacao']   
    
    def retornarSituacao():
        return Matricula.SITUACAO

    def retornarDescricaoSituacao(self):
        for i in range(len(self.SITUACAO)):
            if self.situacao == self.SITUACAO[i][0]:
                return self.SITUACAO[i][1]



                