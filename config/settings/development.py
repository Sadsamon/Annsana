from .base import *  # noqa: F401,F403
import environ

env = environ.Env(DEBUG=(bool, True))
environ.Env.read_env(str(BASE_DIR / ".env"))

SECRET_KEY = env("SECRET_KEY", default="django-insecure-dev-key-do-not-use-in-prod")
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default="postgres://annsana:annsana@localhost:5432/annsana_dev",
    )
}

INSTALLED_APPS += ["django_browser_reload"]  # noqa: F405
MIDDLEWARE += ["django_browser_reload.middleware.BrowserReloadMiddleware"]  # noqa: F405
