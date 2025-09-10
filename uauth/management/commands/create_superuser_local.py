# myapp/management/commands/create_superuser.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

import os
from dotenv import load_dotenv

# 로컬에서만 .env 파일 로드 (환경에 따라 다를 수 있음)
load_dotenv()  # 이 줄을 추가하면 .env 파일에서 환경 변수를 로드합니다.

SUPERUSER_PASSWORD = os.getenv(
    "DJANGO_SUPERUSER_PASSWORD"
)  # 우선 OS 환경 변수에서 찾고

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
