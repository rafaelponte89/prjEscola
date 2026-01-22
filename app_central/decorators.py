# central/decorators.py
from django.contrib.auth.decorators import user_passes_test

def rh_required(view_func):
    return user_passes_test(lambda u: u.groups.filter(name='RH').exists() or u.is_superuser)(view_func)

def aluno_required(view_func):
    return user_passes_test(lambda u: u.groups.filter(name='Aluno').exists() or u.is_superuser)(view_func)
