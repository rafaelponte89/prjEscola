from django.apps import AppConfig
from django.db.utils import OperationalError

class RhConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rh"

   