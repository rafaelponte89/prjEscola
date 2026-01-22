import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Cria superusuário inicial da Central'

    def handle(self, *args, **kwargs):
        username = os.getenv('DJANGO_SU_NAME', 'admin')
        email = os.getenv('DJANGO_SU_EMAIL', 'admin@example.com')
        password = os.getenv('DJANGO_SU_PASSWORD')

        if not password:
            self.stdout.write(self.style.ERROR(
                'Defina a variável DJANGO_SU_PASSWORD'
            ))
            return

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username, email, password)
            self.stdout.write(self.style.SUCCESS('Superusuário criado com sucesso!'))
        else:
            self.stdout.write(self.style.WARNING('Superusuário já existe.'))
