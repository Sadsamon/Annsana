# Annsana — Phase 1 (Foundation)

Per TSD v1.1 §16 / v2.0 §16, Phase 1 delivers: Django project scaffold,
settings, DB config, the `users` app, auth views, and base templates.
The repository contains the active Django foundation and deployment scaffolding. Optional platform infrastructure should be treated as separate, intentionally implemented features rather than assumed defaults.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env: set SECRET_KEY and DATABASE_URL (Postgres 16, per TSD §3)

npm install
npm run build:css        # compiles static/css/output.css from Tailwind tokens

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

- `config/` — Django project package (`settings/base.py`,
  `development.py` / `production.py`, root `urls.py`, `wsgi.py` / `asgi.py`)
- `apps/users/` — authentication, profiles, and user-account logic
- `apps/feed/` — posts, images, likes, comments, and feed rendering
- `templates/` — HTML templates
- `static/` — frontend assets
  Griot flag manageable from Django admin
- `templates/` — `base.html` (nav, Tailwind, HTMX script tag) and a
  placeholder `core/home.html` standing in for `/` until `feed:home`
  exists (Phase 2)
- `tailwind.config.js` / `static/css/input.css` — the "Digital Museum"
  design tokens from TSD §9.1

## Verified working (manual test pass, this session)

- `manage.py check` — clean
- `makemigrations` produces `BigAutoField` PKs as the schema requires
- Full flow exercised against a throwaway SQLite DB: register → auto-created
  `UserProfile` → profile page renders → logout → login → edit profile
  (bio/location persist) → anonymous user redirected away from
  `/profile/edit/` → duplicate username rejected without a 500 → admin
  reachable

## Known follow-ups for later phases (not bugs, just sequencing)

- `UserProfile.recalculate_reputation()` is a stub — wired to real logic
  in Phase 5 once `apps.trust.models.Vote` exists.
- `/` is a placeholder until `apps.feed` lands in Phase 2 — swap the
  `TemplateView` in `config/urls.py` for `feed:home` then, and update
  `LOGIN_REDIRECT_URL` / the nav link if you want it to land somewhere
  more specific than the feed root.
- HTMX is loaded from a CDN (`unpkg.com`) in `base.html` for Phase 1 dev
  convenience. TSD §14 specifies a vendored `static/js/htmx.min.js` —
  swap that in before shipping (cdnjs/unpkg aren't reachable from this
  build sandbox, so it couldn't be vendored here).
