from django.db import models
from aluno.models.aluno import Aluno
from aluno.models.ano import Ano
from aluno.models.classe import Classe


class Matricula(models.Model):
    SITUACAO = (
        ('C', 'CURSANDO'),
        ('BXTR', 'TRANSFERIDO'),
        ('REMA', 'REMANEJADO'),
        ('NCFP', 'Ñ COMP. FORA PRAZO'),
        ('P', 'PROMOVIDO'),
        ('R', 'REPROVADO'),
    )

    ano = models.ForeignKey(
        Ano,
        on_delete=models.RESTRICT
    )

    classe = models.ForeignKey(
        Classe,
        on_delete=models.RESTRICT,
        related_name='matriculas'
    )

    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.RESTRICT,
        related_name='matriculas'
    )

    numero = models.IntegerField(default=0)

    situacao = models.CharField(
        max_length=4,
        choices=SITUACAO,
        default='C'
    )

    data_matricula = models.DateField(null=True, blank=True)
    data_movimentacao = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.aluno} - {self.classe}'

    class Meta:
        unique_together = (
            'ano',
            'aluno',
            'situacao',
            'data_matricula',
            'data_movimentacao',
        )
        indexes = [
            models.Index(fields=['aluno', '-ano']),
        ]

    @staticmethod
    def retornarSituacao():
        return Matricula.SITUACAO

    def retornarDescricaoSituacao(self):
        return dict(self.SITUACAO).get(self.situacao)
