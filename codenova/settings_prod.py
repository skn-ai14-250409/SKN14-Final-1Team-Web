from .settings import *
import os

DEBUG = False

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
ALLOWED_HOST = os.getenv("ALLOWED_HOST", "127.0.0.1")
ALLOWED_HOSTS = [
    ALLOWED_HOST,
]

# 웹 애플리케이션 서버가 리버스 프록시(Reverse Proxy)나 로드 밸런서(Load Balancer) 뒤에서 실행될 때
# 클라이언트가 HTTPS를 통해 연결했음을 Django에 알리는 설정
# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# 모든 HTTP 요청을 HTTPS로 강제 리디렉션(Redirection)시키는 설정
# SECURE_SSL_REDIRECT = True

# # 쿠키 보안 설정
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True

# SECURE_BROWSER_XSS_FILTER = True
# SECURE_CONTENT_TYPE_NOSNIFF = True

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
