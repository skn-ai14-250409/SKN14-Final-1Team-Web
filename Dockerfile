# build dependencies
FROM python:3.12-slim AS builder
WORKDIR /app

ENV PATH=/root/.local/bin:$PATH

# requirements 설치
COPY requirements-prod.txt .
RUN pip install --user --no-cache-dir -r requirements-prod.txt

# HuggingFace 캐시 디렉토리 지정
ENV HF_HOME=/root/.cache/huggingface

# 모델 미리 다운로드 (BAAI/bge-m3)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-m3')"

# runtime image
FROM python:3.12-slim
WORKDIR /app

ENV PATH=/root/.local/bin:$PATH
ENV HF_HOME=/root/.cache/huggingface

# copy only installed packages and cache from builder
COPY --from=builder /root/.local /root/.local
COPY --from=builder /root/.cache/huggingface /root/.cache/huggingface

# copy project files
COPY . .

# collect static files during build
RUN python manage.py collectstatic --noinput

# start gunicorn with custom config
CMD ["sh", "-c", "python manage.py migrate && python manage.py create_superuser && gunicorn -c gunicorn.conf.py"]

EXPOSE 8000
