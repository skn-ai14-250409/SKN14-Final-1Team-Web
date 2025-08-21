# Python 3.12 이미지를 기반으로 사용
FROM python:3.12

# 환경 변수 설정
# .pyc 파일 생성 방지
ENV PYTHONDONTWRITEBYTECODE=1

# Python 출력 버퍼링 방지
ENV PYTHONUNBUFFERED=1

# 작업 디렉토리 생성 및 설정
WORKDIR /app

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 프로젝트 파일을 image 내부 WORKDIR로 복사
COPY . .

# Gunicorn으로 Django 실행
ENTRYPOINT ["gunicorn", "-c", "gunicorn.conf.py"]
EXPOSE 8000