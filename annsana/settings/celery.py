"""
Celery application — Phase 7.

Broker:  Redis (CELERY_BROKER_URL in .env)
Backend: Redis (CELERY_RESULT_BACKEND in .env)

Phase 7 tasks registered here:
  - apps.feed.tasks.process_post_image  (async Pillow resize after upload)

Usage:
  celery -A annsana worker -l info          # start worker
  celery -A annsana beat -l info            # start scheduler (if using periodic tasks)
"""
import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'annsana.settings.development')

app = Celery('annsana')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
