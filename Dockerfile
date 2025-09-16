# build dependencies
FROM python:3.12-slim AS builder
WORKDIR /app

ENV PATH=/root/.local/bin:$PATH

# requirements 설치
COPY requirements-prod.txt .
RUN pip install --user --no-cache-dir -r requirements-prod.txt

# runtime image
FROM python:3.12-slim
WORKDIR /app

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
CMD ["sh", "-c", "python manage.py migrate && python manage.py create_superuser && gunicorn -c gunicorn.conf.py"]

EXPOSE 8000
