# app_central/apps.py
from django.apps import AppConfig
from django.db.models.signals import post_migrate

class CentralConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_central'

