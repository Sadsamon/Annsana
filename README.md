# Annsana — Phase 1 Scaffold

Django project scaffold for Annsana: a platform bridging social expression
(Instagram-style feed) with archival research (wiki-style knowledge base)
around African cultural heritage.

## Stack
Django · PostgreSQL · HTMX · Tailwind CSS

## Structure

```
config/             Project config (split settings, root urls, wsgi/asgi)
apps/users/         Custom user model and profile views
apps/feed/          Posts, multi-image carousels, likes, comments (HTMX)
static/css/tokens.css   Design tokens (color, type, spacing, radii)
tailwind.config.js  Tailwind theme wired to the design tokens
templates/          Base template + app templates
```

## Phase 2 — feed app

- `Post` (caption, location, author) with a separate `PostImage` table so
  multi-image carousels don't require a later schema change.
- `Like` (unique per user/post) and `Comment`, both with HTMX-driven
  partial updates — no full page reload on like or comment.
- `FeedListView` paginates and serves an HTMX partial for infinite scroll
  (`hx-trigger="revealed"` on a sentinel div).
- Known gap: there's no login/signup view yet — `LoginRequiredMixin` and
  `@login_required` will redirect to Django's default `/accounts/login/`,
  which doesn't have a template yet. That's a reasonable candidate for the
  next phase alongside the wiki/archive app.

Run the test suite without a live Postgres connection:

```bash
DJANGO_SETTINGS_MODULE=config.settings.testing python manage.py test
```

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then edit SECRET_KEY / DATABASE_URL
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Settings default to `config.settings.development`. For production, set
`DJANGO_SETTINGS_MODULE=config.settings.production` and provide a real
`SECRET_KEY`, `DATABASE_URL`, and `ALLOWED_HOSTS` via environment variables.

## Tailwind

This scaffold assumes the Tailwind CLI or `django-tailwind` will compile
`tailwind.config.js` into `static/css/main.css`. Design tokens live in
`static/css/tokens.css` as CSS custom properties and are referenced from
`tailwind.config.js` rather than hardcoded, so a future re-theme only
touches one file.
