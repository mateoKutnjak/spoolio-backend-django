import os

from django.conf import settings

from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spoolio_backend.settings")

app = Celery("spoolio_backend")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
