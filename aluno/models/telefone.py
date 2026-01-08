from django.db import models
from aluno.models.aluno import Aluno
#Telefones do aluno
class Telefone(models.Model):
    TEL_CHOICES = (
        ('M', 'MÃE'),
        ('P', 'PAI'),
        ('T', 'TIA/TIO'),
        ('I', 'IRMÃ/IRMÃO'),
        ('A', 'AVÓ/AVÔ'),
        ('R', 'RESPONSÁVEL'),
        ('O', 'OUTRO'),
    )

    aluno = models.ForeignKey(Aluno, on_delete=models.RESTRICT, related_name="telefones")
    contato = models.CharField(max_length=1, choices=TEL_CHOICES)
    numero = models.CharField(max_length=11, default='')

    def __str__(self):
        return self.numero

    @classmethod
    def retornarListaTelefones(cls):
        return cls.TEL_CHOICES
