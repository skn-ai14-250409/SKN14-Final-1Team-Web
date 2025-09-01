# Contributing Guidelines

이 프로젝트의 실행을 위한 가이드라인 입니다.

# 실행방법

```python
conda create -n codenova python=3.12 -y
conda activate codenova
pip install -r requirements.txt
```

# 로컬 실행 방법

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

# 도커 실행방법

```bash
$ docker build -t codenova-web . 
$ docker run -d --name codenova-web --env-file .env -p 8000:8000 codenova-web
```
