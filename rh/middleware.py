# rh/middleware.py
from django.shortcuts import redirect

class RHAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/rh/') and not (request.user.is_superuser or request.user.groups.filter(name='RH').exists()):
            return redirect('login')  # ou página de "acesso negado"
        return self.get_response(request)


