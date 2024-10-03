# inventory/management/commands/run_scheduled_outbounds.py

from django.core.management.base import BaseCommand
from inventory.views import automated_outbound_check
import time

class Command(BaseCommand):
    help = 'Continuously process scheduled outbounds in real time'

    def handle(self, *args, **kwargs):
        try:
            while True:
                automated_outbound_check()
                self.stdout.write(self.style.SUCCESS('Processed scheduled outbounds.'))
                time.sleep(60)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Stopping scheduled outbound processing.'))
