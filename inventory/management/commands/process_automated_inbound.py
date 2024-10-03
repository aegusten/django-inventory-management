from django.core.management.base import BaseCommand
from inventory.views import automated_inbound_check

class Command(BaseCommand):
    help = 'Process automated inbound based on inventory levels'

    def handle(self, *args, **kwargs):
        automated_inbound_check()
        self.stdout.write(self.style.SUCCESS('Automated inbound process completed.'))
