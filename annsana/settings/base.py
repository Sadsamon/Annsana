"""
Base settings for the Annsana project.

Shared across development.py and production.py. Never import this file
directly when running the server — use one of the environment-specific
modules so DEBUG and ALLOWED_HOSTS are set deliberately.
"""
from pathlib import Path

import environ

# --- Paths -------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# --- Environment ---------------------------------------------------------------
env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY', default='insecure-development-key-do-not-use-in-prod')

# --- Application Definition ---------------------------------------------------
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'django_htmx',
    'crispy_forms',
    'crispy_tailwind',
]

# NOTE: feed / archive / linking / trust are added here in Phases 2–5.
LOCAL_APPS = [
    'apps.users',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
]

ROOT_URLCONF = 'annsana.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'annsana.wsgi.application'

# --- Database ------------------------------------------------------------------
DATABASES = {
    'default': env.db('DATABASE_URL', default='postgres://annsana:annsana@localhost:5432/annsana'),
}

# --- Password Validation ---------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- Internationalization ---------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- Static Files (Section 9) -----------------------------------------------------
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    # NOTE: this is intentionally the plain backend, not WhiteNoise's
    # manifest one. ManifestStaticFilesStorage requires `collectstatic` to
    # have already run, or {% static %} raises a "missing manifest entry"
    # error — which would break every page in local development before a
    # single collectstatic run. production.py overrides this.
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}

# --- Media Files (Section 10) -----------------------------------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp']
MAX_UPLOAD_SIZE_MB = 10

# --- Default PK Field --------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Auth Redirects -----------------------------------------------------------------
LOGIN_URL = 'users:login'
LOGIN_REDIRECT_URL = 'users:profile_detail_self'
# NOTE: redirects to login for now since the feed app doesn't exist until
# Phase 2 — reverse('feed:home') would raise NoReverseMatch if set today.
# Change this to 'feed:home' the moment Phase 2 lands.
LOGOUT_REDIRECT_URL = 'users:login'

# --- Crispy Forms (Tailwind pack) ----------------------------------------------------
CRISPY_ALLOWED_TEMPLATE_PACKS = 'tailwind'
CRISPY_TEMPLATE_PACK = 'tailwind'

# --- Annsana Business Rules (TSD Section 12) -----------------------------------------
# These thresholds belong to the Trust Layer (built in Phase 5) but are defined
# here from day one so they are never hardcoded into view logic later.
ENTRY_VERIFICATION_THRESHOLD = env.int('ENTRY_VERIFICATION_THRESHOLD', default=3)
LINK_VERIFICATION_THRESHOLD = env.int('LINK_VERIFICATION_THRESHOLD', default=2)
GRIOT_THRESHOLD = env.int('GRIOT_THRESHOLD', default=100)
