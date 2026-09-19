# ── Build stage ───────────────────────────────────────────────────────
FROM python:3.12-slim AS build

WORKDIR /app

# System deps for Pillow and psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev libjpeg-dev zlib1g-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Runtime stage ─────────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 libjpeg62-turbo \
 && rm -rf /var/lib/apt/lists/*

# Copy installed packages from build stage
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

# Copy project
COPY . .

# Collect static files (media goes to S3 in production)
RUN python manage.py collectstatic --noinput --settings=config.settings.production
# Non-root user for security
RUN adduser --disabled-password --gecos '' annsana \
 && chown -R annsana:annsana /app
USER annsana

EXPOSE 8000

# Gunicorn: 1 worker per CPU + 1, non-blocking I/O via gevent
CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--timeout", "60", \
     "--access-logfile", "-"]
