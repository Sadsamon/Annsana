from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    label = 'users'
    verbose_name = 'Users & Profiles'

    def ready(self):
        # Import signal handlers so they register on app startup.
        from . import signals  # noqa: F401
