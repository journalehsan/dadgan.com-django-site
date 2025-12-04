from django.apps import AppConfig


class LawfirmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lawfirm'

    def ready(self):
        import lawfirm.signals  # Import signals when app is ready
