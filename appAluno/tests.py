from django.test import TestCase
from .models import Aluno
from .views import gravar
from django.test.client import Client
from django.urls import reverse
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render

# Create your tests here.

class AlunoModelTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        for i in range(1,11):
            Aluno.objects.create(rm=i, nome="Aluno Teste"+str(i))
    
    
    def test_nome(self):
        aluno = Aluno.objects.get(rm=1)
        self.assertEqual(aluno.nome, "Aluno Teste1")
    
    def test_representacao(self):
        aluno = Aluno.objects.get(rm=1)
        representacao = aluno.__str__()
        self.assertEqual(representacao, '[1] Aluno Teste1')
    
    def test_retornar_ultimos(self):
        alunos = Aluno.objects.order_by('-rm')[:5]
        lista_inversa = [10,9,8,7,6]
        i = 0
        for a in alunos:
            self.assertAlmostEqual(a.rm, lista_inversa[i])
            i += 1

class AlunoViewTest(TestCase):
    pass
   

            
        
        
        
        
        
