# 로컬 개발환경
from .settings import *

DEBUG = True

ALLOWED_HOSTS = []

# 개발 db
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}