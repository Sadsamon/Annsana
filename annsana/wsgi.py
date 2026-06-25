"""WSGI config for Annsana. Used by gunicorn in production."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'annsana.settings.production')

application = get_wsgi_application()
