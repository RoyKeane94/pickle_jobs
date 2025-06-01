from django.apps import AppConfig


class EmploymentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'employment'

    def ready(self):
        import employment.signals
