from .base import *  # noqa: F401,F403
import environ

env = environ.Env()
environ.Env.read_env(str(BASE_DIR / ".env"))

SECRET_KEY = env("SECRET_KEY")
DEBUG = False
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

DATABASES = {"default": env.db("DATABASE_URL")}

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
