from __future__ import absolute_import

import os

from celery import Celery
from celery.schedules import crontab

from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'penguins.settings')

app = Celery('penguins')
app.conf.update(
    BROKER_URL='redis://localhost:6379/1',
    CELERY_RESULT_BACKEND='redis://localhost:6379/1',
    CELERY_TIMEZONE = 'UTC',
    CELERY_IMPORTS = ('observations.tasks',)
)
