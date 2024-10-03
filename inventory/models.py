# inventory/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('Manager', 'Manager'),
        ('Operator', 'Operator'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.username} ({self.role})"

class Customer(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    contact_person = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)
    supplier = models.CharField(max_length=255)
    tags = models.CharField(max_length=255, blank=True)
    reorder_point = models.PositiveIntegerField(default=0)
    overstock_point = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.sku} - {self.name}"

    @property
    def available_quantity(self):
        return self.quantity - self.reserved_quantity

class ScheduledOutbound(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    scheduled_date = models.DateTimeField()
    destination = models.CharField(max_length=255)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Scheduled Outbound for {self.customer.name} on {self.scheduled_date}"

class Inbound(models.Model):
    reference = models.CharField(max_length=50)
    date_received = models.DateTimeField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    location = models.CharField(max_length=100)
    remarks = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='inbounds_created',
        on_delete=models.SET_NULL,
        null=True
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='inbounds_modified',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Inbound {self.reference} - {self.product}"

CATEGORY_CHOICES = [
    ('Sale', 'Sale'),
    ('Internal Transfer', 'Internal Transfer'),
]

STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Shipped', 'Shipped'),
    ('Delivered', 'Delivered'),
    ('Canceled', 'Canceled')
]

class Outbound(models.Model):
    reference = models.CharField(max_length=50)
    date_shipped = models.DateTimeField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    destination = models.CharField(max_length=255)
    customer_name = models.CharField(max_length=255, blank=True)
    remarks = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='outbounds_created',
        on_delete=models.SET_NULL,
        null=True
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='outbounds_modified',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Outbound {self.reference} - {self.product.sku} to {self.customer_name} ({self.status})"
