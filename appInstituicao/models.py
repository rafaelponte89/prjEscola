from django.db import models

# Create your models here.

class Instituicao (models.Model):
    instituicao = models.CharField(max_length=100, blank=False, unique=True)
    email = models.EmailField(max_length=100)
    telefone_fixo_publico = models.CharField(max_length=11)
    endereco = models.CharField(max_length=200)

    def __str__(self):
        return self.instituicao