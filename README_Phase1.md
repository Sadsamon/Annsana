# Annsana — Phase 1: Foundation

This is the Phase 1 scaffold described in the Annsana TSD (Section 16):
Django project setup, environment-split settings, PostgreSQL config,
the `users` app (registration, login/logout, profiles, Griot flag),
and base templates wired to the Tailwind design system.

## Setup

```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# edit .env: set SECRET_KEY, DATABASE_URL, etc.

# 4. Install frontend tooling and build Tailwind CSS
npm install
npm run build:css
# during development, use the watcher instead:
# npm run watch:css

# 5. Create the Postgres database (adjust to your local setup)
createdb annsana

# 6. Run migrations
python manage.py makemigrations
python manage.py migrate

# 7. Create a superuser (this is also how you promote a user to Griot later)
python manage.py createsuperuser

# 8. Run the dev server
python manage.py runserver
```

Visit `http://127.0.0.1:8000/register/` to create an account, or
`/admin/` to log in as your superuser and flip `is_griot = True` on a
`UserProfile`.

## What's in this phase

- `annsana/settings/` — split into `base.py`, `development.py`, `production.py`
- `apps/users/` — `UserProfile` model, registration/login/logout views,
  profile view + edit view, admin registration, auto-profile-creation signal
- `templates/base.html` — global nav, flash messages, Tailwind design tokens
- `tailwind.config.js` / `static/css/input.css` — design system from TSD §9.1

## What's deliberately deferred

Per the TSD's phased plan and the architect's notes already on file:

- Image resize/WebP pipeline is **not yet wired to `Post.save()`** because
  `Post` doesn't exist until Phase 2. `UserProfile.avatar` is stored as-is
  for now; revisit with `django-imagekit` if upload volume grows.
- `UserProfile.recalculate_reputation()` is implemented but is a safe no-op
  until the `trust` app (Phase 5) exists — it looks up the `Vote` model by
  name via `apps.get_model()` rather than importing it directly, so no
  changes will be needed here when Phase 5 lands.
- Griot promotion is manual-only via `/admin/`, as decided.
- `feed`, `archive`, `linking`, `trust` apps are not yet created — their
  `INSTALLED_APPS` entries and `urls.py` includes are left as commented
  placeholders so the wiring is obvious when each phase begins.

## Next step

Phase 2 — the `feed` app: `Post` model, image upload pipeline, feed home
view, and HTMX infinite scroll.
