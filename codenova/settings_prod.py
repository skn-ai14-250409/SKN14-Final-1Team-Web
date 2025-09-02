from .settings import *
import os

DEBUG = False

ALLOWED_HOST = os.getenv("ALLOWED_HOST", "127.0.0.1")
ALLOWED_HOSTS = [
    ALLOWED_HOST,
]

# 배포 DB 설정
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# CORS 설정
INSTALLED_APPS += [
    "corsheaders",
]

MIDDLEWARE.insert(0, "corsheaders.middleware.CorsMiddleware")

# 허용할 CORS Origin
CORS_ORIGIN_ALLOW_ALL = True

# 인증 관련 헤더 허용
CORS_ALLOW_CREDENTIALS = True
