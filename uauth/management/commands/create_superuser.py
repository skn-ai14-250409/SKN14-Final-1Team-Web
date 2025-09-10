# myapp/management/commands/create_superuser.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

import os

SUPERUSER_PASSWORD = os.getenv("DJANGO_SUPERUSER_PASSWORD")  # OS 환경변수

# uauth/management/commands/create_superuser.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create a superuser if not already exists"

    def handle(self, *args, **kwargs):
        User = get_user_model()
        if not User.objects.filter(id="admin").exists():
            User.objects.create_superuser(
                id="admin",
                email="admin@example.com",
                password=SUPERUSER_PASSWORD,
                name="Admin User",
                phone="1234567890",
                gender="male",
                birthday="2000-01-01",
                rank="cto",
            )
            self.stdout.write(self.style.SUCCESS("Superuser created successfully"))
        else:
            self.stdout.write(self.style.SUCCESS("Superuser already exists"))
