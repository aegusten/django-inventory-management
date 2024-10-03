from django.core.management.base import BaseCommand
from inventory.models import Product, Outbound, InventoryTransaction
from django.utils import timezone
from django.db.models import F
from django.db import transaction

class Command(BaseCommand):
    help = 'Automated outbound process based on inventory levels'

    def handle(self, *args, **kwargs):
        overstocked_products = Product.objects.filter(quantity__gte=F('overstock_point'))
        for product in overstocked_products:
            quantity_to_ship = product.quantity - product.overstock_point
            if quantity_to_ship > 0:
                try:
                    with transaction.atomic():
                        outbound = Outbound.objects.create(
                            reference=f"AUTO-OUTBOUND-{product.sku}-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                            date_shipped=timezone.now(),
                            product=product,
                            quantity=quantity_to_ship,
                            destination='Automated Clearance',
                            customer_name='System Generated',
                            category='Sale',
                            status='Shipped',
                            created_by=None
                        )

                        product.quantity -= quantity_to_ship
                        product.save()

                        InventoryTransaction.objects.create(
                            product=product,
                            action='Outbound',
                            quantity=-quantity_to_ship,
                            user=None,
                            remarks='Automated outbound due to overstock.'
                        )

                        self.stdout.write(self.style.SUCCESS(f"Automated outbound created for product {product.sku}."))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error processing product {product.sku}: {str(e)}"))
        self.stdout.write(self.style.SUCCESS('Automated outbound process completed.'))
