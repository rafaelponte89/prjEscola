from django.db import models


# Create your models here.
# Aluno
class Aluno (models.Model):
    
    STATUS_ARQUIVADO = 0
    STATUS_CANCELADO = 1
    STATUS_ATIVO = 2

    STATUS_CHOICES = (
        (STATUS_ARQUIVADO, "Arquivado"),
        (STATUS_CANCELADO, "Cancelado"),
        (STATUS_ATIVO, "Ativo"),
    )
    
    rm = models.IntegerField(primary_key=True,)
    nome = models.CharField(max_length=150)
    #status (0 - arquivado, 1 - cancelado, 2 - ativo) 
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_ATIVO, db_default=0)
    ra = models.CharField(max_length=100, default='')
    d_ra = models.CharField(max_length=1, default='', null=True, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
 
    def __str__(self):
        return f'{self.nome}'
    
    @property
    def is_ativo(self):
        return self.status == self.STATUS_ATIVO

    @property
    def is_cancelado(self):
        return self.status == self.STATUS_CANCELADO

    @property
    def is_arquivado(self):
        return self.status == self.STATUS_ARQUIVADO
    
    # Retorna o último aluno no banco de dados
    @classmethod
    def retornarUltimo(cls):
        aluno = cls.objects.last()
        return aluno
    
    @classmethod
    def retornarNUltimos(cls, n=6):
        alunos = cls.objects.order_by('-rm')[:n]
        return alunos
    
    class Meta:
        app_label = 'aluno'
    

#Documentos do aluno (NÃO IMPLEMENTADO)
class Prontuario(models.Model):
    DOCUMENTO_CHOICES = (
        ('CN','Certidão de Nascimento'),
        ('RGA','RG - Aluno'),
        ('CPFA','CPF - Aluno'),
        ('CV','Carteira Vacinação'),
        ('RGR','RG - Responsável'),
        ('CPFR','CPF - Responsável'),
        ('CNH','CNH'),
        ('FM','Ficha de Matrícula'),
        ('CR','Comprovante de Residência'),
        ('LD','Laudo'),
        ('OT','Outros')
    )
    #aluno = models.ForeignKey(Aluno)
    descricao = models.CharField(max_length=4, choices=DOCUMENTO_CHOICES, blank=False, null=False, default='') 
    caminho = models.ImageField()
    
    class Meta:
        app_label = 'aluno'

    
    

    