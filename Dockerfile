FROM python:3.11-slim-bookworm

WORKDIR /app

RUN useradd --create-home --uid 1000 kb

COPY pyproject.toml README.md ./
COPY kb_server ./kb_server

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

ENV KB_HOST=0.0.0.0 \
    KB_PORT=8080 \
    KB_CONTENT_PATH=/kb/content \
    KB_DB_PATH=/kb/data/kb.db \
    KB_REINDEX_ON_STARTUP=true

RUN mkdir -p /kb/data /kb/content && chown -R kb:kb /kb /app

USER kb
EXPOSE 8080

CMD ["uvicorn", "kb_server.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8080"]
