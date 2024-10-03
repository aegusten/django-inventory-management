# inventory/management/commands/automated_inbound.py

from django.core.management.base import BaseCommand
from inventory.models import Product, Inbound
from django.utils import timezone
from django.db.models import F

class Command(BaseCommand):
    help = 'Automated inbound process based on inventory levels'

    def handle(self, *args, **kwargs):
        low_stock_products = Product.objects.filter(quantity__lte=F('reorder_point'))
        for product in low_stock_products:
            Inbound.objects.create(
                reference=f"AUTO-INBOUND-{product.sku}-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                date_received=timezone.now(),
                product=product,
                quantity=50,
                location=product.location,
                remarks='Automated inbound due to low stock.'
            )
            product.quantity += 50
            product.save()
        self.stdout.write(self.style.SUCCESS('Automated inbound process completed.'))
