from django.apps import AppConfig


class SettingsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "settings"

    def ready(self):
        # Importing signals here ensures they’re registered without triggering database access
        import settings.signals
