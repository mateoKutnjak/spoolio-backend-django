from django.apps import AppConfig


class UserProfileConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'spoolio_backend.apps.user_profile'

    def ready(self) -> None:
        from spoolio_backend.apps.user_profile import signals
        return super().ready()