# gunicorn 실행옵션 python 변수로 선언
import multiprocessing

# workers 워커프로세스 개수
workers = multiprocessing.cpu_count() * 2 + 1
print('workers =', workers)

# bind 주소/포트
bind = '0.0.0.0:8000'

# worker_class 기본값:sync(동기워커)
worker_class = 'uvicorn.workers.UvicornWorker'

# wsgi_app 실행한 모듈 application
wsgi_app = 'codenova.asgi:application'