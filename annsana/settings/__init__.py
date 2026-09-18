# Load Celery at startup when it's available (not a hard dep in dev).
try:
    from .celery import app as celery_app  # noqa: F401
    __all__ = ['celery_app']
except ImportError:
    pass  # Celery not installed — fine for local dev without Redis.
