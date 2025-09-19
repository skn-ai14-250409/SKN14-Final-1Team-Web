# build dependencies
FROM python:3.12-slim AS builder
WORKDIR /app

ENV PATH=/root/.local/bin:$PATH

RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# requirements 설치
COPY requirements-prod.txt .
RUN pip install --user --no-cache-dir -r requirements-prod.txt

# runtime image
FROM python:3.12-slim
WORKDIR /app

# 런타임에 필요한 mysqlclient 라이브러리 설치
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 환경 변수 설정
# .pyc 파일 생성 방지
ENV PYTHONDONTWRITEBYTECODE=1

# Python 출력 버퍼링 방지
ENV PYTHONUNBUFFERED=1

# copy only installed packages from builder
ENV PATH=/root/.local/bin:$PATH
COPY --from=builder /root/.local /root/.local

# copy project files
COPY . .

# collect static files during build
RUN python manage.py collectstatic --noinput

# start gunicorn with custom config
ENTRYPOINT ["gunicorn", "-c", "gunicorn.conf.py"]

EXPOSE 8000
