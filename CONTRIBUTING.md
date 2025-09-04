# Contributing Guidelines

이 프로젝트의 실행을 위한 가이드라인 입니다.

# 실행방법

가상환경 설정하기

```python
conda create -n codenova python=3.12 -y
conda activate codenova
pip install -r requirements.txt

# black 코드 포멧팅 설정
pre-commit install
```

`.env` 설정하기

```
OPENAI_API_KEY = your_api_key
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

# 도커 허브이미지 실행방법

```bash
$ docker pull skn14f1/codenova
$ docker run -d --name codenova --env-file .env -p 8000:8000 skn14f1/codenova
```
