# inventory/admin.py

from django.contrib import admin
from .models import Customer, ScheduledOutbound

admin.site.register(Customer)
admin.site.register(ScheduledOutbound)
