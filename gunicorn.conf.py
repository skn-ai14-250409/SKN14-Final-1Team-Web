# gunicorn 실행옵션 python 변수로 선언
import multiprocessing


# workers 워커프로세스 개수
workers = min(multiprocessing.cpu_count(), 1)
print("workers =", workers)

# bind 주소/포트
bind = "0.0.0.0:8000"

# worker_class 기본값:sync(동기워커)
worker_class = "uvicorn.workers.UvicornWorker"

timeout = 300
graceful_timeout = 30
keepalive = 75

preload_app = False
max_requests = 1000
max_requests_jitter = 100


# wsgi_app 실행한 모듈 application
wsgi_app = "codenova.asgi:application"
