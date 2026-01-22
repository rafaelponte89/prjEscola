from django.shortcuts import redirect

class AlunoAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/aluno/') and not (request.user.is_superuser or request.user.groups.filter(name='Aluno').exists()):
            return redirect('login')  # ou página de "acesso negado"
        return self.get_response(request)