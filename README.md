# Annsana

A community-focused platform connecting social expression (a feed) with an archival research knowledge base focused on African cultural heritage.

<img src="1.png" title="1" alt="Annsana placeholder screenshot" width="720" style="max-width:100%;height:auto;" />

---

## Overview

Annsana is a Django-based scaffold that provides a starting point for building a social feed (multi-image posts, likes, comments) alongside a wiki-style archival repository for curated research materi[...]

---

## Quick facts

- Stack: Django · PostgreSQL · HTMX · Tailwind CSS
- Status: Phase 1 scaffold (feed app under active development)
- License: Apache-2.0 (see LICENSE)

---

## Contents

- config/ — project configuration (split settings: development / testing / production)
- apps/ — application packages (users, feed, etc.)
- static/ — compiled frontend assets and design tokens
- templates/ — Django templates
- docs/ — documentation assets and screenshots

---

## Getting started (development)

1. Create a virtual environment and activate it:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies and prepare environment:

```bash
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env      # edit SECRET_KEY, DATABASE_URL, ALLOWED_HOSTS
```

3. Run migrations and start the development server:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Use `config.settings.development` for local development and `config.settings.production` for production deployments.

---

## Testing

Local unit tests can be run against the testing settings:

```bash
DJANGO_SETTINGS_MODULE=config.settings.testing python -m pytest -q
```

---

## Contributing

See CONTRIBUTING.md for contribution guidelines and the project's Code of Conduct. Small fixes, documentation improvements, and issues are welcome.

---

## Images & branding

The `docs/` directory contains placeholder images. Replace these with project screenshots before publishing the repository or enabling GitHub Pages.

---

## License

This repository is licensed under the Apache License, Version 2.0. See the LICENSE file for details.
