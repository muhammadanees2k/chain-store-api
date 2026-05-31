# store/apps.py
from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        # This tells Django to load your signals when the app starts
        import store.signals
