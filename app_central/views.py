from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.user.is_authenticated:
        return redirect('central')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('central')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')

    return render(request, 'app_central/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def home_view(request):
    """
    Central do sistema. Define flags para acesso aos blocos
    Aluno e RH baseado nos grupos do usuário.
    """
    user = request.user
    grupos = user.groups.values_list('name', flat=True)

    context = {
        'pode_acessar_rh': 'RH' in grupos or user.is_superuser,
        'pode_acessar_aluno': 'Aluno' in grupos or user.is_superuser,
    }

    return render(request, 'app_central/central.html', context)
