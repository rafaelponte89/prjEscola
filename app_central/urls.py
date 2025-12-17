from django.urls.conf import path

from .views import central

urlpatterns = [
     path('', central, name='central'),
]