"""Development settings. Loaded via DJANGO_SETTINGS_MODULE in manage.py / .env."""
from .base import *  # noqa: F401, F403
from .base import env

DEBUG = True

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

# Verbose error pages and no HTTPS enforcement locally.
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Makes debugging slow queries / N+1 issues easier (Section 13 performance budget).
INSTALLED_APPS += []  # placeholder: add 'debug_toolbar' here if/when adopted
