# gunicorn 실행옵션 python 변수로 선언
import multiprocessing


# # workers 워커프로세스 개수
# workers = multiprocessing.cpu_count() * 2 + 1
# print("workers =", workers)
#
# # bind 주소/포트
# bind = "0.0.0.0:8000"
#
# # worker_class 기본값:sync(동기워커)
# worker_class = "uvicorn.workers.UvicornWorker"
#
# # wsgi_app 실행한 모듈 application
# wsgi_app = "codenova.asgi:application"



# gunicorn.conf.py — 안전 기본값 (ASGI + 큰 모델)
bind = "0.0.0.0:8000"

# 워커 2개로 줄임
workers = 1

# ASGI용 워커
worker_class = "uvicorn.workers.UvicornWorker"

# 타임아웃 여유 (첫 모델 로딩 보호)
timeout = 300
graceful_timeout = 30
keepalive = 75

# 메모리 누수 대비(선택)
max_requests = 1000
max_requests_jitter = 100

# 로그(필요시)
loglevel = "warning"
accesslog = "-"
errorlog = "-"

# wsgi_app 실행한 모듈 application
wsgi_app = "codenova.asgi:application"