"""
Django settings for codenova project.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Security / Debug ---
SECRET_KEY = (
    "django-insecure-ob*oa=#dhgf32a#g@i*7eovc7#znjfs^!i8t!^92%dgw4z39dy"  # 개발용
)
DEBUG = True
ALLOWED_HOSTS = []

# --- Apps ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "main",
    "uauth",
    "apichat",
    "mypage",
    "internal"
]

AUTH_USER_MODEL = "uauth.User"

# --- Middleware ---
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "codenova.urls"

# --- Templates ---
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # main/templates 를 전역 템플릿 디렉터리로 사용
        "DIRS": [BASE_DIR / "main" / "templates"],
        "APP_DIRS": True,  # 각 앱의 templates/도 자동 탐색
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "codenova.wsgi.application"

# --- Database ---
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
# MySQL 사용 시 아래 예시 사용
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'codenovadb',
#         'USER': 'django',
#         'PASSWORD': 'django',
#         'HOST': '127.0.0.1',
#         'PORT': '3306',
#         'OPTIONS': {'charset': 'utf8mb4'},
#     }
# }

# --- Auth password validators ---
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- I18N / TZ ---
LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True

# --- Static / Media ---
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"  # collectstatic 결과물
STATICFILES_DIRS = [BASE_DIR / "main" / "static"]  # 개발용 정적 소스

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# --- Defaults ---
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


from django.urls import reverse_lazy

LOGIN_URL = reverse_lazy("uauth:login")  # 루트('/')로 resolve됨 (현 구조에서)
LOGIN_REDIRECT_URL = reverse_lazy("main:home")  # 실제 라우트 이름에 맞게
LOGOUT_REDIRECT_URL = reverse_lazy("uauth:login")



