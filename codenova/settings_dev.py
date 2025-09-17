import os
from .settings import *
from dotenv import load_dotenv

load_dotenv()

DEBUG = False

ALLOWED_HOST = os.getenv("ALLOWED_HOST", "127.0.0.1")
ALLOWED_HOSTS = [
    ALLOWED_HOST,
]

# 개발 db
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("MYSQL_DATABASE", "codenovadb"),
        "USER": os.environ.get("MYSQL_USER", "django"),
        "PASSWORD": os.environ.get("MYSQL_PASSWORD", "django"),
        "HOST": os.environ.get("MYSQL_HOST", "127.0.0.1"),
        "PORT": os.environ.get("MYSQL_PORT", "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
        },
    }
}

LOGGING = {
    # 파이썬 로깅 설정 버전 항상 1로 고정.
    "version": 1,
    # 기존에 만들어진 로거를 끄지 않겠다는 의미
    # 장고가 기본으로 만드는 django, django.request 등 로거가 살아 있음
    # True로 하면 장고 기본 로거까지 꺼져서 로그가 안 나올 수 있음
    "disable_existing_loggers": False,
    # 로그 메시지의 출력 형식 정의
    # [INFO] 2025-09-16 08:15:23 myapp.views: hello_view 호출됨
    "formatters": {
        "verbose": {
            "format": "[{levelname}] {asctime} {name}: {message}",
            "style": "{",
        },
    },
    # 로그를 어디로 보낼지 정의
    # "console" → stdout(터미널) 출력
    # "level": "DEBUG" → 최소 DEBUG 이상 로그부터 처리
    # "formatter": "verbose" → 위에서 만든 포맷 사용
    # StreamHandler → 표준 출력(console)용
    # EB 환경에서는 stdout → /var/log/web.stdout.log / CloudWatch로 자동 수집됨
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    # 이름 없는 기본 로거
    # 내가 만든 코드(logging.getLogger(__name__))에서 로거 이름이 별도로 없으면 root가 처리
    # "handlers": ["console"] → console로 출력
    # "level": "INFO" → INFO 이상 로그 처리
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
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
