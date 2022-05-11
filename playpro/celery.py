import os
from datetime import timedelta

from celery.schedules import crontab
from django.conf import settings

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "playpro.settings")
app = Celery("playpro")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.conf.broker_url = settings.CELERY_BROKER_URL
app.conf.worker_send_task_events = True
app.conf.task_send_sent_event = True
app.conf.beat_schedule = {
    "ping": {
        "task": "playpro.celery.debug_task",
        "schedule": timedelta(minutes=1),
    },
    "autocreate_matches": {
        "task": "tournaments.create_tournament_groups_or_ladder",
        "schedule": timedelta(minutes=5),
    },
}


@app.task()
def debug_task():
    print("PING")
