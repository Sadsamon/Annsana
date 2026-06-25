"""
Lightweight settings for running the test suite without a live Postgres
instance. Use with: DJANGO_SETTINGS_MODULE=config.settings.testing
"""

from .development import *  # noqa: F401,F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test_db.sqlite3",  # noqa: F405
    }
}
