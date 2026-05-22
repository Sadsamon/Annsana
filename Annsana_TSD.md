# HeritageHub — Technical Specification Document (TSD)
**Version:** 1.0 — MVP  
**Classification:** Internal Architecture Reference  
**Author:** Senior Software Architect  
**Date:** 2026-05-22  

---

## Table of Contents
1. [Project Summary](#1-project-summary)
2. [System Architecture Overview](#2-system-architecture-overview)
3. [Technology Stack](#3-technology-stack)
4. [Application Modules](#4-application-modules)
5. [Database Schema](#5-database-schema)
6. [URL & Routing Structure](#6-url--routing-structure)
7. [API Contract (HTMX Endpoints)](#7-api-contract-htmx-endpoints)
8. [Authentication & Permissions](#8-authentication--permissions)
9. [Frontend Architecture](#9-frontend-architecture)
10. [File & Media Handling](#10-file--media-handling)
11. [The Linking Engine](#11-the-linking-engine)
12. [The Trust Layer (Verification System)](#12-the-trust-layer-verification-system)
13. [Non-Functional Requirements](#13-non-functional-requirements)
14. [Project Directory Structure](#14-project-directory-structure)
15. [MVP Scope & Out-of-Scope](#15-mvp-scope--out-of-scope)
16. [Development Phases](#16-development-phases)

---

## 1. Project Summary

HeritageHub is a digital cultural preservation platform centered on African heritage. It operates on two interconnected pillars:

| Pillar | Description | Analogy |
|---|---|---|
| **The Social Feed** | User-generated posts — photos, videos, cultural moments | Instagram |
| **The Knowledge Archive** | Expert-authored articles on traditions, recipes, history | Wikipedia |
| **The Bridge** | Dynamic, verified links between posts and archive entries | The core innovation |

The platform's unique value is the **programmatic relationship** between lived cultural expression (a photo of Sadza) and structured cultural knowledge (the history and recipe of Sadza). Every architectural decision must serve this bridge.

---

## 2. System Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                         CLIENT BROWSER                           │
│          HTML5 + Tailwind CSS + HTMX (partial page swaps)        │
└──────────────────────┬───────────────────────────────────────────┘
                       │ HTTP / HTMX requests
┌──────────────────────▼───────────────────────────────────────────┐
│                     DJANGO APPLICATION SERVER                     │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │  users   │  │  feed    │  │ archive  │  │    linking       │ │
│  │  app     │  │  app     │  │  app     │  │    engine        │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘ │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  trust (verification) app                │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────┬───────────────────────────────────────────┘
                       │ ORM
┌──────────────────────▼───────────────────────────────────────────┐
│                       POSTGRESQL DATABASE                         │
└──────────────────────────────────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────────┐
│                  MEDIA STORAGE (local/S3-compatible)              │
│               Post images, Archive images                         │
└──────────────────────────────────────────────────────────────────┘
```

**Pattern:** Monolithic Django application with a modular app structure. No microservices at MVP stage. HTMX handles all dynamic interactions via server-rendered HTML fragments — no SPA, no separate REST API for the frontend.

---

## 3. Technology Stack

| Layer | Technology | Version | Rationale |
|---|---|---|---|
| Backend Framework | Django | 5.x | Batteries-included, ORM, admin, auth |
| Database | PostgreSQL | 16.x | Relational integrity for links; full-text search |
| Frontend Interaction | HTMX | 2.x | Progressive enhancement; low-JS; performant on slow connections |
| CSS Framework | Tailwind CSS | 3.x | Utility-first; consistent "Digital Museum" aesthetic |
| Python | Python | 3.12+ | Required for Django 5 |
| Media Storage (dev) | Django `MEDIA_ROOT` | — | Local filesystem |
| Media Storage (prod) | S3-compatible (Cloudflare R2 or AWS S3) | — | Scalable, cheap egress |
| Environment Config | `django-environ` | — | `.env` based configuration |
| Forms | `django-crispy-forms` + crispy-tailwind | — | Tailwind-compatible form rendering |
| Image Processing | `Pillow` | — | Thumbnail generation, validation |
| Dev Server | `gunicorn` | — | Production-ready WSGI |

---

## 4. Application Modules

The Django project is named `heritagehub`. It contains five discrete applications, each owning its domain:

### 4.1 `users` App
**Responsibility:** Authentication, profiles, roles, reputation.

Models: `UserProfile`  
Key Views: `register`, `login`, `logout`, `profile_detail`, `profile_edit`  
Role System: Standard `User` → elevated to `Griot` via admin flag on `UserProfile`.

### 4.2 `feed` App
**Responsibility:** The social layer — post creation, display, hashtags, categories, geolocations.

Models: `Post`, `Hashtag`, `Category`  
Key Views: `feed_home`, `post_create`, `post_detail`, `post_delete`  
HTMX Patterns: Infinite scroll on the feed; inline post creation form.

### 4.3 `archive` App
**Responsibility:** The knowledge layer — article creation, rich content, schemas for recipes/guidelines.

Models: `ArchiveEntry`, `RecipeSchema`, `GuidelineSchema`  
Key Views: `archive_home`, `entry_create`, `entry_detail`, `entry_edit`  
Access Control: Only `Griot`-role users may create/edit Archive Entries.

### 4.4 `linking` App
**Responsibility:** The Bridge — managing many-to-many relationships between Posts and Archive Entries.

Models: `PostArchiveLink`  
Key Views: `link_create`, `link_remove`, `linked_entries_fragment` (HTMX partial)  
Logic: Any authenticated user can suggest a link; Griots verify it.

### 4.5 `trust` App
**Responsibility:** The Trust Layer — voting and verification on Archive Entries and Links.

Models: `Vote`, `VerificationStatus`  
Key Views: `vote_cast` (HTMX), `verification_status_fragment` (HTMX partial)  
Logic: Reputation score aggregated from received upvotes; Griot threshold configurable via `settings.py`.

---

## 5. Database Schema

### 5.1 `users_userprofile`

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | |
| `user_id` | `INTEGER` | FK → `auth_user`, UNIQUE | One-to-one |
| `bio` | `TEXT` | NULLABLE | |
| `avatar` | `VARCHAR(255)` | NULLABLE | Media path |
| `is_griot` | `BOOLEAN` | DEFAULT `FALSE` | Role flag |
| `reputation_score` | `INTEGER` | DEFAULT `0` | Aggregated trust score |
| `location` | `VARCHAR(100)` | NULLABLE | Self-reported location |
| `created_at` | `TIMESTAMPTZ` | DEFAULT `NOW()` | |

---

### 5.2 `feed_category`

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | |
| `name` | `VARCHAR(100)` | UNIQUE, NOT NULL | e.g., "Food", "Attire", "Rituals" |
| `slug` | `VARCHAR(100)` | UNIQUE, NOT NULL | URL-safe identifier |
| `description` | `TEXT` | NULLABLE | |

---

### 5.3 `feed_hashtag`

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | |
| `name` | `VARCHAR(100)` | UNIQUE, NOT NULL | Stored without `#` |

---

### 5.4 `feed_post`

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | |
| `author_id` | `INTEGER` | FK → `auth_user` | |
| `caption` | `TEXT` | NOT NULL | |
| `image` | `VARCHAR(255)` | NULLABLE | Media path |
| `category_id` | `BIGINT` | FK → `feed_category`, NULLABLE | |
| `geolocation` | `VARCHAR(200)` | NULLABLE | Free-text location string |
| `latitude` | `DECIMAL(9,6)` | NULLABLE | Future map use |
| `longitude` | `DECIMAL(9,6)` | NULLABLE | Future map use |
| `created_at` | `TIMESTAMPTZ` | DEFAULT `NOW()` | |
| `updated_at` | `TIMESTAMPTZ` | AUTO | |
| `is_published` | `BOOLEAN` | DEFAULT `TRUE` | Soft delete mechanism |

**Relationships:**
- `feed_post` ↔ `feed_hashtag`: M2M via `feed_post_hashtags` join table

---

### 5.5 `archive_archiveentry`

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | |
| `author_id` | `INTEGER` | FK → `auth_user` | Must be `is_griot=True` |
| `title` | `VARCHAR(255)` | NOT NULL | |
| `slug` | `VARCHAR(255)` | UNIQUE, NOT NULL | Auto-generated from title |
| `body` | `TEXT` | NOT NULL | Supports Markdown/HTML |
| `category_id` | `BIGINT` | FK → `feed_category` | Shared category taxonomy |
| `entry_type` | `VARCHAR(50)` | NOT NULL | ENUM: `'article'`, `'recipe'`, `'guideline'` |
| `cover_image` | `VARCHAR(255)` | NULLABLE | Media path |
| `is_verified` | `BOOLEAN` | DEFAULT `FALSE` | Set by Trust Layer |
| `created_at` | `TIMESTAMPTZ` | DEFAULT `NOW()` | |
| `updated_at` | `TIMESTAMPTZ` | AUTO | |

---

### 5.6 `archive_recipeschema`

Attached to an `ArchiveEntry` with `entry_type = 'recipe'`.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | |
| `entry_id` | `BIGINT` | FK → `archive_archiveentry`, UNIQUE | One-to-one |
| `ingredients` | `JSONB` | NOT NULL | `[{"item": "...", "quantity": "..."}]` |
| `instructions` | `TEXT` | NOT NULL | Step-by-step |
| `prep_time_minutes` | `INTEGER` | NULLABLE | |
| `cook_time_minutes` | `INTEGER` | NULLABLE | |
| `serves` | `INTEGER` | NULLABLE | |
| `region_of_origin` | `VARCHAR(150)` | NULLABLE | |

---

### 5.7 `archive_guidelineschema`

Attached to an `ArchiveEntry` with `entry_type = 'guideline'`.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | |
| `entry_id` | `BIGINT` | FK → `archive_archiveentry`, UNIQUE | One-to-one |
| `steps` | `JSONB` | NOT NULL | `[{"step": 1, "description": "..."}]` |
| `occasions` | `VARCHAR(255)` | NULLABLE | Comma-separated tags |
| `required_items` | `TEXT` | NULLABLE | |

---

### 5.8 `linking_postarchivelink`

The Bridge table. Central to the platform's value proposition.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | |
| `post_id` | `BIGINT` | FK → `feed_post` | |
| `entry_id` | `BIGINT` | FK → `archive_archiveentry` | |
| `suggested_by_id` | `INTEGER` | FK → `auth_user` | Who created the link |
| `is_verified` | `BOOLEAN` | DEFAULT `FALSE` | Griot-verified link |
| `created_at` | `TIMESTAMPTZ` | DEFAULT `NOW()` | |

**Constraint:** `UNIQUE(post_id, entry_id)` — no duplicate links.

---

### 5.9 `trust_vote`

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | |
| `voter_id` | `INTEGER` | FK → `auth_user` | |
| `vote_type` | `VARCHAR(10)` | NOT NULL | ENUM: `'up'`, `'down'` |
| `target_type` | `VARCHAR(20)` | NOT NULL | ENUM: `'entry'`, `'link'` |
| `target_entry_id` | `BIGINT` | FK → `archive_archiveentry`, NULLABLE | |
| `target_link_id` | `BIGINT` | FK → `linking_postarchivelink`, NULLABLE | |
| `created_at` | `TIMESTAMPTZ` | DEFAULT `NOW()` | |

**Constraint:** `UNIQUE(voter_id, target_type, target_entry_id)` and `UNIQUE(voter_id, target_type, target_link_id)` — one vote per target.

---

## 6. URL & Routing Structure

```
heritagehub/
│
├── /                           → feed:home (the social feed)
├── /register/                  → users:register
├── /login/                     → users:login
├── /logout/                    → users:logout
├── /profile/<username>/        → users:profile_detail
├── /profile/edit/              → users:profile_edit
│
├── /posts/
│   ├── create/                 → feed:post_create
│   ├── <id>/                   → feed:post_detail
│   └── <id>/delete/            → feed:post_delete
│
├── /archive/
│   ├── /                       → archive:home
│   ├── create/                 → archive:entry_create  [Griot only]
│   ├── <slug>/                 → archive:entry_detail
│   └── <slug>/edit/            → archive:entry_edit    [Griot only]
│
├── /links/
│   ├── create/                 → linking:link_create
│   ├── <id>/remove/            → linking:link_remove
│   └── post/<post_id>/entries/ → linking:linked_entries_fragment [HTMX]
│
└── /trust/
    ├── vote/                   → trust:vote_cast       [HTMX POST]
    └── status/<target>/        → trust:status_fragment [HTMX GET]
```

---

## 7. API Contract (HTMX Endpoints)

These endpoints return HTML fragments, not JSON. They are consumed exclusively by HTMX attributes in templates.

| Endpoint | Method | HTMX Trigger | Returns | Target |
|---|---|---|---|---|
| `/trust/vote/` | `POST` | Button click | Vote count fragment | `#vote-count-{id}` |
| `/links/post/<id>/entries/` | `GET` | Page load / click | Linked entries cards | `#linked-entries` |
| `/links/create/` | `POST` | Form submit | Updated links list | `#linked-entries` |
| `/posts/create/` | `POST` | Form submit | New post card | `#feed-top` (prepend) |
| Feed scroll | `GET` | `intersect` event | Next page of posts | `#feed-container` (append) |

All HTMX endpoints must:
1. Check `request.htmx` (via `django-htmx`) and return a 400 if called directly.
2. Return appropriate `HX-Trigger` response headers for client-side events where needed (e.g., `HX-Trigger: postCreated`).

---

## 8. Authentication & Permissions

### Role Hierarchy

```
Anonymous User
    │  can: Browse feed, browse archive
    │
    ▼
Authenticated User
    │  can: Create posts, suggest links, cast votes
    │
    ▼
Griot (is_griot = True)
       can: All of the above + create/edit Archive Entries + verify links/entries
```

### Django Permission Strategy

- Use Django's built-in `LoginRequiredMixin` for all write operations.
- Create a custom `GriotRequiredMixin` that checks `request.user.userprofile.is_griot`.
- Griot status is set **only by Django admin** at MVP. No self-promotion mechanism.
- All permission failures return an HTMX-aware redirect (check `HX-Request` header to return a `HX-Redirect` response instead of a standard 302).

### Session Security

- `SESSION_COOKIE_HTTPONLY = True`
- `SESSION_COOKIE_SECURE = True` (production)
- `CSRF_COOKIE_SECURE = True` (production)
- Django's built-in CSRF protection applies to all HTMX POST requests (include `{% csrf_token %}` in all forms or set the `hx-headers` meta tag globally).

---

## 9. Frontend Architecture

### 9.1 Design System

The UI follows a **"Digital Museum meets Modern Social Network"** aesthetic. All design tokens are defined in `tailwind.config.js`.

```javascript
// tailwind.config.js — HeritageHub Design Tokens
theme: {
  extend: {
    colors: {
      'earth':    { 900: '#2C1810', 700: '#5C3D2E', 400: '#A0785A', 100: '#F5EDE4' },
      'terracotta': { DEFAULT: '#C0693B', light: '#D4845E' },
      'sage':     { DEFAULT: '#6B7C5E', light: '#8A9E7A' },
      'parchment': { DEFAULT: '#F8F2E8', dark: '#EDE4D3' },
      'ink':      { DEFAULT: '#1A1A2E', soft: '#4A4A6A' },
    },
    fontFamily: {
      'display': ['"Playfair Display"', 'serif'],  // Headings, archive titles
      'body':    ['"Inter"', 'sans-serif'],         // UI, captions
    }
  }
}
```

### 9.2 Template Hierarchy

```
templates/
├── base.html                    # Root: nav, footer, HTMX script, Tailwind CDN/build
├── components/
│   ├── post_card.html           # Reusable post card partial
│   ├── archive_card.html        # Reusable archive entry card
│   ├── link_badge.html          # "Linked to Archive" badge on posts
│   ├── vote_widget.html         # Up/down vote buttons with HTMX
│   └── griot_badge.html         # Griot indicator
├── feed/
│   ├── home.html
│   ├── post_detail.html
│   └── post_create.html
├── archive/
│   ├── home.html
│   ├── entry_detail.html
│   └── entry_form.html
├── users/
│   ├── profile.html
│   ├── login.html
│   └── register.html
└── partials/                    # HTMX-only fragments (no base extension)
    ├── feed_page.html
    ├── linked_entries.html
    ├── vote_count.html
    └── link_list.html
```

### 9.3 HTMX Configuration (Global)

Place in `base.html` `<head>`:
```html
<meta name="htmx-config" content='{"defaultSwapStyle": "innerHTML", "historyCacheSize": 10}'>
<!-- CSRF for all HTMX requests -->
<meta name="htmx-config" content='{"defaultHeaders": {"X-CSRFToken": "{{ csrf_token }}"}}'>
```

---

## 10. File & Media Handling

### Settings

```python
MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Allowed upload types
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp']
MAX_UPLOAD_SIZE_MB  = 10
```

### Image Processing Pipeline (Post Creation)

1. User uploads image via form.
2. Django view receives `request.FILES['image']`.
3. `Pillow` validates MIME type and dimensions.
4. Image resized to max `1200px` on longest side; WebP conversion for storage efficiency.
5. Thumbnail generated at `400x400` for feed cards.
6. Both saved to `media/posts/<year>/<month>/`.

### Archive Entry Images

- Cover images follow the same pipeline, saved to `media/archive/<year>/<month>/`.
- Max dimensions: `1600px` wide.

---

## 11. The Linking Engine

The Linking Engine is the platform's most critical module. It governs how social content connects to archival knowledge.

### Flow

```
Post Created
    │
    ▼
Author (or any user) navigates to Post Detail
    │
    ├─► "Link to Archive" button opens search fragment (HTMX GET)
    │         │
    │         ▼
    │   Live search of Archive Entries by title/category
    │         │
    │         ▼
    │   User selects an entry → HTMX POST → creates PostArchiveLink (is_verified=False)
    │
    ▼
Link appears on Post with "Unverified" badge
    │
    ▼
Griot sees unverified link → casts an "up" vote on the link
    │
    ▼
trust.signals.py: When upvote threshold reached → set PostArchiveLink.is_verified=True
    │
    ▼
"Verified" badge appears on link
```

### Business Rules

- A Post can link to **multiple** Archive Entries.
- An Archive Entry can be linked from **multiple** Posts.
- Duplicate `(post_id, entry_id)` pairs are rejected at the DB constraint level.
- Only **Griots** can verify links. Regular users can suggest links.
- A Griot cannot verify their own suggested link.

---

## 12. The Trust Layer (Verification System)

### Reputation Score Logic

```
UserProfile.reputation_score =
    SUM of upvotes received on Archive Entries authored by the user
  + SUM of upvotes received on Links suggested by the user
  - SUM of downvotes received on same targets
```

Reputation is recalculated via a Django signal (`post_save` on `Vote`) and cached on the `UserProfile` row for performance.

### Griot Promotion (MVP)

- Manual: Django superuser sets `userprofile.is_griot = True` via admin.
- Future: Automated promotion when `reputation_score >= GRIOT_THRESHOLD` (configurable in `settings.py`, default: `100`).

### Verification Threshold

An `ArchiveEntry` is marked `is_verified = True` when:
- It has received **>= 3 upvotes** from distinct Griot users.

A `PostArchiveLink` is marked `is_verified = True` when:
- It has received **>= 2 upvotes** from distinct Griot users.

These thresholds are stored as Django settings constants:

```python
ENTRY_VERIFICATION_THRESHOLD = 3
LINK_VERIFICATION_THRESHOLD  = 2
```

---

## 13. Non-Functional Requirements

### Performance

| Requirement | Target |
|---|---|
| Feed page initial load (3G) | < 3 seconds |
| HTMX partial response time | < 500ms |
| Image upload processing time | < 2 seconds |
| Database query count per page | < 15 (enforced by Django Debug Toolbar in dev) |

**Strategies:**
- `select_related` and `prefetch_related` on all feed/archive querysets.
- Thumbnail display in feeds (full image only on detail view).
- Django template fragment caching for the Archive home page (`cache` templatetag).
- PostgreSQL indexes on `feed_post.created_at`, `archive_archiveentry.slug`, `linking_postarchivelink(post_id, entry_id)`.

### Accessibility

- All images require `alt` text (enforced in forms via a required `alt_text` field on `Post`).
- Tailwind's `focus:ring` utilities applied to all interactive elements.
- Semantic HTML5: `<main>`, `<article>`, `<section>`, `<nav>`, `<aside>` used correctly.
- Minimum colour contrast ratio: 4.5:1 (WCAG AA).

### Security

- `DEBUG = False` in production; enforced via `django-environ`.
- `ALLOWED_HOSTS` explicitly set from environment variables.
- File uploads validated server-side (MIME type + magic bytes, not just extension).
- Django's `SecurityMiddleware` enabled with HSTS, `X-Frame-Options: DENY`.
- Rate limiting on post creation and voting endpoints via `django-ratelimit`.

---

## 14. Project Directory Structure

```
heritagehub/                    # Project root
├── manage.py
├── requirements.txt
├── .env.example
├── tailwind.config.js
│
├── heritagehub/                # Django project config package
│   ├── __init__.py
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
│
├── apps/
│   ├── users/
│   │   ├── models.py           # UserProfile
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   └── templates/users/
│   │
│   ├── feed/
│   │   ├── models.py           # Post, Hashtag, Category
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   └── templates/feed/
│   │
│   ├── archive/
│   │   ├── models.py           # ArchiveEntry, RecipeSchema, GuidelineSchema
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   └── templates/archive/
│   │
│   ├── linking/
│   │   ├── models.py           # PostArchiveLink
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── templates/linking/
│   │
│   └── trust/
│       ├── models.py           # Vote
│       ├── views.py
│       ├── signals.py          # Reputation recalculation
│       ├── urls.py
│       └── templates/trust/
│
├── templates/
│   ├── base.html
│   ├── components/
│   └── partials/
│
├── static/
│   ├── css/
│   │   └── output.css          # Tailwind compiled output
│   └── js/
│       └── htmx.min.js
│
└── media/                      # Dev only; gitignored
```

---

## 15. MVP Scope & Out-of-Scope

### ✅ In Scope (MVP)

- User registration, login, logout
- User profile page (view only)
- Post creation with text caption and single image upload
- Category and hashtag tagging on posts
- Feed home page (chronological, paginated via HTMX infinite scroll)
- Archive Entry creation (Title, Body, Category) — Griot only
- Archive Entry detail page
- Post → Archive Entry link creation and display
- Upvote/downvote on Archive Entries
- Upvote/downvote on Post-Archive Links
- Reputation score display on user profile
- Django admin for all models
- Basic `is_griot` flag and Griot-only view guards

### ❌ Out of Scope (Post-MVP)

- Video upload and playback
- Comments on posts or archive entries
- Direct messaging
- Geolocation map view
- Recipe/Guideline schema forms (schema models are built, but UI forms deferred)
- Automated Griot promotion
- Email notifications
- Full-text search (PostgreSQL `tsvector`)
- Social follow system
- Content moderation / reporting tools
- Mobile app (React Native)
- S3 media storage (local filesystem at MVP)

---

## 16. Development Phases

| Phase | Description | Key Deliverables |
|---|---|---|
| **Phase 1** | Foundation | Django project scaffold, settings, DB, `users` app, auth views, base templates |
| **Phase 2** | Social Feed | `feed` app — Post model, CRUD views, image upload, feed display, HTMX scroll |
| **Phase 3** | The Archive | `archive` app — ArchiveEntry model, Griot-gated forms, entry detail view |
| **Phase 4** | The Bridge | `linking` app — PostArchiveLink model, link suggest/display UI, link badges on posts |
| **Phase 5** | The Trust Layer | `trust` app — Vote model, signals, reputation scoring, verification badges |
| **Phase 6** | Polish & Harden | Design system refinement, performance audit, security hardening, Django admin customisation |

Each phase produces a working, testable vertical slice of the application before the next phase begins.

---

*This document is the authoritative technical reference for HeritageHub MVP development. All subsequent module builds must conform to the schemas, naming conventions, and architectural decisions defined herein.*
