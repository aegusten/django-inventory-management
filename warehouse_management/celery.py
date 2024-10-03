# warehouse_management/celery.py

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'warehouse_management.settings')

app = Celery('warehouse_management')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
