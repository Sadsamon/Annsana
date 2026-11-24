# Annsana

Annsana is a digital platform that bridges social expression and archival
research, with a focus on preserving and celebrating African cultures. It
pairs a social feed with a structured cultural archive, so posts and archival
entries can be linked rather than living in separate silos.

## Highlights

- **Social feed and accounts** — user accounts and profiles, posts with
  images, likes, and comments
- **Archive and feed linked** — a bridge model connects social posts to
  archival entries
- **Async media pipeline** — image processing runs in Celery workers behind a
  Redis broker (Pillow), so uploads return immediately and workers scale
  independently of the web tier
- **Versioned REST API** — Django REST Framework endpoints secured with
  OAuth2/JWT, with Redis-backed rate limiting
- **Delivery pipeline** — containerized with Docker; GitHub Actions CI/CD
  runs automated tests, including the auth and rate-limiting flows

## Architecture

```
request path   client (HTMX + Tailwind) -> Django 5 + DRF v1 -> PostgreSQL 16
async path     Django -> Redis broker -> Celery workers (Pillow) -> processed media
```

## Stack

Django 5, Django REST Framework, PostgreSQL 16, Celery, Redis, HTMX,
Tailwind CSS, Docker, GitHub Actions

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env      # set SECRET_KEY and DATABASE_URL (PostgreSQL 16)

npm install
npm run build:css         # compiles static/css/output.css from the Tailwind config

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

To run the full stack in containers:

```bash
docker compose up --build
```

## Project structure

```
config/       Django project package (settings, root URLs, WSGI/ASGI)
apps/         Django apps, one per domain (users, feed, ...)
templates/    HTML templates
static/       Tailwind source and compiled CSS
docs/         Design and technical documentation
tests/        Test suite
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## License

See [LICENSE](LICENSE).
