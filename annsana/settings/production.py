"""
Production settings.

Security posture follows TSD Section 13. ALLOWED_HOSTS, SECRET_KEY, and
DATABASE_URL must always come from the environment — never hardcode them.
"""
from .base import *  # noqa: F401, F403
from .base import env

DEBUG = False

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')  # No default: must be explicit in production.

# --- HTTPS / Transport Security ---
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# --- Clickjacking / Content Sniffing ---
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True

# --- Proxy Awareness (if deployed behind a load balancer / reverse proxy) ---
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# --- Static Files ---
# Switch to WhiteNoise's manifest storage here, not in base.py — this
# backend requires `collectstatic` to have run, which is a production-only
# step in our deploy process (see README). Using it in development would
# break {% static %} before the first collectstatic call.
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}

# --- Media Storage ---
# At MVP this still resolves to FileSystemStorage from base.py (TSD: local
# filesystem at MVP). Swap the 'default' STORAGES backend to an S3-compatible
# one (e.g. django-storages with Cloudflare R2) when media volume justifies it.
