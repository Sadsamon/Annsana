"""ASGI config for Annsana. Not used at MVP but kept for forward compatibility."""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'annsana.settings.production')

application = get_asgi_application()
