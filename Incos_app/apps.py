from django.apps import AppConfig


class IncosAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Incos_app' # <--- ESTO DEBE COINCIDIR EXACTAMENTE
    verbose_name = 'Sistema de Préstamos INCOS'