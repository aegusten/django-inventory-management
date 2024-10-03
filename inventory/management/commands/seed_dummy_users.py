# File: inventory/management/commands/seed_dummy_users.py
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from inventory.models import User

class Command(BaseCommand):
    help = 'Seed the database with dummy users (Admin, Manager, and Operator)'

    def handle(self, *args, **kwargs):
        # List of dummy users
        users_data = [
            {
                'username': 'admin',
                'email': 'admin@gmail.com',
                'password': make_password('admin'),  # Hash the password
                'role': 'Admin',
                'is_superuser': True,
                'is_staff': True,
            },
            {
                'username': 'manager',
                'email': 'manager@gmail.com',
                'password': make_password('manager'),  # Hash the password
                'role': 'Manager',
                'is_superuser': False,
                'is_staff': True,
            },
            {
                'username': 'operator',
                'email': 'operator@gmail.com',
                'password': make_password('operator'),  # Hash the password
                'role': 'Operator',
                'is_superuser': False,
                'is_staff': False,
            }
        ]

        for user_data in users_data:
            if not User.objects.filter(username=user_data['username']).exists():
                user = User.objects.create(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                )
                user.role = user_data['role']
                user.is_superuser = user_data['is_superuser']
                user.is_staff = user_data['is_staff']
                user.save()
                self.stdout.write(self.style.SUCCESS(f"User {user.username} created."))
            else:
                self.stdout.write(self.style.WARNING(f"User {user_data['username']} already exists."))

        self.stdout.write(self.style.SUCCESS('Dummy users have been successfully added!'))
