# build dependencies
FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# runtime image
FROM python:3.12-slim
WORKDIR /app

# copy only installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# copy project files
COPY . .

# collect static files during build
RUN python manage.py collectstatic --noinput
RUN python -c "from apichat.utils.vector_db import create_chroma_db; create_chroma_db()"
# RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-m3')"

# expose container port
EXPOSE 8000

# start gunicorn with custom config
ENTRYPOINT ["gunicorn", "-c", "gunicorn.conf.py"]