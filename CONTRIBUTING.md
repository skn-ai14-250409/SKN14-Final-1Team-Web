# Contributing Guidelines

이 프로젝트의 실행을 위한 가이드라인 입니다.

# 실행방법

가상환경 설정하기

```python
conda create -n codenova-web python=3.12 -y
conda activate codenova-web
pip install -r requirements-dev.txt
pip install -r requirements-prod.txt

# black 코드 포멧팅 설정
pre-commit install
```

`.env` 설정하기

```
# 장고 설정
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_key
AWS_S3_REGION_NAME=your_aws_name
AWS_STORAGE_BUCKET_NAME=your_aws_name
AWS_STORAGE_BUCKET_NAME2=your_aws_name
OPENAI_API_KEY=sk-xxxx
SLLM_API_URL=custom
DJANGO_SUPERUSER_PASSWORD=custom

# 장고 배포 설정
ALLOWED_HOST=*
DJANGO_SETTINGS_MODULE=codenova.settings_dev

# MYSQL 도커 설정
MYSQL_ROOT_PASSWORD=custom

# MYSQL 도커 설정 및 장고 디비 설정
MYSQL_DATABASE=custom
MYSQL_USER=custom
MYSQL_PASSWORD=custom

# 장고 디비 설정
MYSQL_HOST=localhost
MYSQL_PORT=3306
```

# 로컬 실행 방법

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py create_superuser_local
python manage.py runserver 0.0.0.0:8000
```

# 도커 실행방법

```bash
docker run -d --name codenova-mysql --env-file .env -p 3306:3306 mysql:8.0 \
  --bind-address=0.0.0.0 \
  --lower_case_table_names=1

docker build -t codenova-web .
docker run -d --name codenova-web --env-file .env -p 8000:8000 codenova-web
```

# 도커 허브이미지 실행방법

```bash
docker pull skn14f1/codenova
docker run -d --name codenova --env-file .env -p 8000:8000 skn14f1/codenova
```
