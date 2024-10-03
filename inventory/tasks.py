# inventory/tasks.py

from celery import shared_task
from .views import automated_outbound_check

@shared_task
def process_scheduled_outbounds():
    automated_outbound_check()
