# build dependencies
FROM python:3.12-slim AS builder
WORKDIR /app

ENV PATH=/root/.local/bin:$PATH
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# runtime image
FROM python:3.12-slim
WORKDIR /app

# copy only installed packages from builder
ENV PATH=/root/.local/bin:$PATH
COPY --from=builder /root/.local /root/.local

# copy project files
COPY . .

# collect static files during build
RUN python manage.py collectstatic --noinput
# RUN python -c "from apichat.utils.vector_db import create_chroma_db; create_chroma_db()"
# RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-m3')"

CMD ["sh", "-c", "python manage.py migrate && gunicorn -c gunicorn.conf.py"]
EXPOSE 8000

# start gunicorn with custom config
CMD ["sh", "-c", "python manage.py migrate && gunicorn -c gunicorn.conf.py"]
# ENTRYPOINT ["gunicorn", "-c", "gunicorn.conf.py"]