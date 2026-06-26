# Annsana — Technical Specification Document (TSD)
**Version:** 2.0 — Integration-Ready Architecture
**Classification:** Internal Architecture Reference
**Author:** Senior Software Architect
**Date:** 2026-06-26

---

## Revision Note

Version 2.0 evolves the v1.1 MVP (a self-contained HTMX monolith) into an
**integration-ready, secure, and scalable platform**. Four capabilities are
added in this revision:

1. A versioned, public-facing **REST API** (Django REST Framework) exposing
   the Archive and Linking domains for third-party integration.
2. **Asynchronous image processing** via Celery + Redis, removing the
   synchronous Pillow pipeline from the request/response cycle.
3. **Enterprise-grade API security** — JWT access/refresh tokens with
   rotation and blacklisting, scoped API clients, and Redis-backed
   throttling on abuse-prone endpoints.
4. **Docker-based deployment** with S3-compatible object storage and
   environment-based secret management.

Every existing database constraint, schema, and architectural decision from
v1.1 is preserved. Nothing here is a breaking change to the v1.1 MVP — this
is a pure extension. Where an earlier Architect's Note is superseded by this
revision, it is marked **`[SUPERSEDED]`** rather than deleted, so the
reasoning trail stays intact.

---

## Table of Contents
1. [Project Summary](#1-project-summary)
2. [System Architecture Overview](#2-system-architecture-overview)
3. [Technology Stack](#3-technology-stack)
4. [Application Modules](#4-application-modules)
5. [Database Schema](#5-database-schema)
6. [URL & Routing Structure](#6-url--routing-structure)
7. [API Contracts](#7-api-contracts)
8. [Authentication & Permissions](#8-authentication--permissions)
9. [Frontend Architecture](#9-frontend-architecture)
10. [File & Media Handling](#10-file--media-handling)
11. [The Linking Engine](#11-the-linking-engine)
12. [The Trust Layer (Verification System)](#12-the-trust-layer-verification-system)
13. [Non-Functional Requirements](#13-non-functional-requirements)
14. [Project Directory Structure](#14-project-directory-structure)
15. [MVP Scope & Out-of-Scope](#15-mvp-scope--out-of-scope)
16. [Development Phases](#16-development-phases)
17. [Deployment Architecture (Docker)](#17-deployment-architecture-docker)

---

## 1. Project Summary

Annsana is a digital cultural preservation platform centered on African heritage. It operates on two interconnected pillars:

| Pillar | Description | Analogy |
|---|---|---|
| **The Social Feed** | User-generated posts — photos, videos, cultural moments | Instagram |
| **The Knowledge Archive** | Expert-authored articles on traditions, recipes, history | Wikipedia |
| **The Bridge** | Dynamic, verified links between posts and archive entries | The core innovation |

The platform's unique value is the **programmatic relationship** between lived cultural expression (a photo of Sadza) and structured cultural knowledge (the history and recipe of Sadza). Every architectural decision must serve this bridge.

As of v2.0, that value is no longer confined to Annsana's own UI: the Archive
and the Bridge are now reachable by museums, researchers, and partner
applications through a public API — extending the preservation mission
beyond Annsana's own front end.

---

## 2. System Architecture Overview

```
┌──────────────────────────────┐   ┌──────────────────────────────────┐
│       CLIENT BROWSER          │   │     THIRD-PARTY INTEGRATIONS      │
│  HTML5 + Tailwind + HTMX      │   │  Museums, researchers, partner   │
│  (session-authenticated)      │   │  apps (JWT-authenticated)        │
└───────────────┬───────────────┘   └─────────────────┬─────────────────┘
                │ HTTP / HTMX                          │ HTTPS / JSON
┌───────────────▼──────────────────────────────────────▼─────────────────┐
│                         DJANGO APPLICATION SERVER                       │
│                                                                         │
│  ┌─────────┐ ┌────────┐ ┌─────────┐ ┌──────────┐ ┌───────┐ ┌─────────┐ │
│  │  users  │ │  feed  │ │ archive │ │ linking  │ │ trust │ │  core   │ │
│  │  app    │ │  app   │ │  app    │ │  engine  │ │ app   │ │ (shared)│ │
│  └─────────┘ └────────┘ └─────────┘ └──────────┘ └───────┘ └─────────┘ │
│                                                                         │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │   api app — DRF gateway: /api/v1/   (JWT auth, throttling,     │   │
│  │   versioning, OpenAPI schema)                                   │   │
│  └────────────────────────────────────────────────────────────────┘   │
└───────┬─────────────────────────────┬───────────────────────┬─────────┘
        │ ORM                          │ enqueue task           │ enqueue task
┌───────▼───────────────┐   ┌──────────▼───────────┐   ┌────────▼─────────┐
│   POSTGRESQL DATABASE  │   │   REDIS                │   │  CELERY WORKER(S) │
│  (+ token blacklist,   │   │  • Celery broker/result│◄──┤  Image validation, │
│   APIClient tables)    │   │  • Throttle cache       │   │  resize, WebP,      │
└────────────────────────┘   │    (separate DB index) │   │  thumbnailing        │
                              └─────────────────────────┘   └─────────┬────────┘
                                                                       │ writes
                                                          ┌────────────▼────────────┐
                                                          │  S3-COMPATIBLE STORAGE   │
                                                          │  (AWS S3 / Cloudflare R2)│
                                                          │  Post + Archive images   │
                                                          └──────────────────────────┘
```

**Pattern:** Still a modular Django **monolith** — we are not introducing
microservices. What's changing is that the monolith now has **two distinct
ingress paths** (session-authenticated HTMX views, and a versioned JWT-
authenticated JSON API) and **one offloaded execution path** (Celery workers
for anything that shouldn't block a request thread). This is the standard,
proven way to scale a Django monolith before microservices are ever
justified — and at Annsana's current scale, microservices are not justified.

> **✅ Architect's Note — Why Not Microservices:**
> Splitting `archive` or `linking` into separate services would buy
> independent deployability at the cost of distributed transactions across
> the Linking Engine's foreign keys — exactly the kind of cross-domain
> integrity the v1.1 TSD called "non-negotiable" for `linking_postarchivelink`.
> A modular monolith with a clean API gateway gets us third-party
> integration without that cost. Revisit only if a single app's scaling
> needs diverge sharply from the others (e.g., `feed` needing to scale
> writes 50x while `archive` stays flat).

---

## 3. Technology Stack

| Layer | Technology | Version | Rationale |
|---|---|---|---|
| Backend Framework | Django | 5.x | Batteries-included, ORM, admin, auth |
| Database | PostgreSQL | 16.x | Relational integrity for links; full-text search |
| Frontend Interaction | HTMX | 2.x | Progressive enhancement; low-JS; performant on slow connections |
| CSS Framework | Tailwind CSS | 3.x | Utility-first; consistent "Digital Museum" aesthetic |
| Python | Python | 3.12+ | Required for Django 5 |
| Environment Config | `django-environ` | — | `.env` / container-env based configuration |
| Forms | `django-crispy-forms` + crispy-tailwind | — | Tailwind-compatible form rendering |
| Image Processing | `Pillow` | — | Validation, resize, WebP conversion (now run inside Celery tasks) |
| **API Framework** | **Django REST Framework** | **3.15.x** | Mature, batteries-included viewsets/serializers/throttling; integrates cleanly with SimpleJWT |
| **API Docs/Schema** | **drf-spectacular** | latest | Auto-generated OpenAPI 3 schema + Swagger UI for third-party integrators |
| **JWT Auth** | **djangorestframework-simplejwt** | 5.x | Short-lived access tokens; rotating + blacklisted refresh tokens |
| **CORS** | **django-cors-headers** | latest | Explicit origin allowlist for cross-origin API consumers |
| **Task Queue** | **Celery** | 5.x | Decouples image processing from the request/response cycle |
| **Broker / Cache** | **Redis** | 7.x | Celery broker + result backend; also backs distributed throttle counters (separate logical DB index — see §10) |
| **Object Storage** | **django-storages** + `boto3` | latest | S3-compatible media storage (AWS S3 or Cloudflare R2) |
| **Containerization** | **Docker** + Docker Compose | — | Reproducible builds; dev/staging/prod parity |
| Rate Limiting (web) | `django-ratelimit` | — | Protects HTMX endpoints (e.g. voting); now Redis-backed for multi-replica correctness |
| Rate Limiting (API) | DRF Throttling (`ScopedRateThrottle`) | built-in | Per-scope limits layered on the same Redis cache |
| Dev/Prod Server | `gunicorn` | — | Production-ready WSGI; one container role among several (see §17) |

---

## 4. Application Modules

The Django project is named `annsana`. It now contains **seven** discrete applications:

### 4.1 `users` App
**Responsibility:** Authentication, profiles, roles, reputation.

Models: `UserProfile`
Key Views: `register`, `login`, `logout`, `profile_detail`, `profile_edit`
Role System: Standard `User` → elevated to `Griot` via admin flag on `UserProfile`.

*Unchanged in v2.0.*

### 4.2 `feed` App
**Responsibility:** The social layer — post creation, display, hashtags, categories, geolocations.

Models: `Post`, `Hashtag`, `Category`
Key Views: `feed_home`, `post_create`, `post_detail`, `post_delete`
HTMX Patterns: Infinite scroll on the feed; inline post creation form.

**v2.0 change:** `Post` image handling no longer processes synchronously in
the view. See §10.

### 4.3 `archive` App
**Responsibility:** The knowledge layer — article creation, rich content, schemas for recipes/guidelines.

Models: `ArchiveEntry`, `RecipeSchema`, `GuidelineSchema`
Key Views: `archive_home`, `entry_create`, `entry_detail`, `entry_edit`
Access Control: Only `Griot`-role users may create/edit Archive Entries.

**v2.0 addition:** `archive/serializers.py` and `archive/viewsets.py` expose
`ArchiveEntry` (read-only by default) to the public API. Domain logic stays
in this app — the `api` app only aggregates routing, auth, and policy.

### 4.4 `linking` App
**Responsibility:** The Bridge — managing many-to-many relationships between Posts and Archive Entries.

Models: `PostArchiveLink`
Key Views: `link_create`, `link_remove`, `linked_entries_fragment` (HTMX partial)
Logic: Any authenticated user can suggest a link; Griots verify it.

**v2.0 addition:** `linking/serializers.py` and `linking/viewsets.py` expose
`PostArchiveLink` to the public API — reads are open; writes require a
scoped, authenticated `APIClient` and still land as `is_verified=False`,
subject to the same Griot review as web-suggested links. See §11.

### 4.5 `trust` App
**Responsibility:** The Trust Layer — voting and verification on Archive Entries and Links.

Models: `Vote`, `VerificationStatus`
Key Views: `vote_cast` (HTMX), `verification_status_fragment` (HTMX partial)
Logic: Reputation score aggregated from received upvotes; Griot threshold configurable via `settings.py`.

**v2.0 decision:** `Vote` is **deliberately excluded** from the public API
surface. See the Architect's Note in §12.

### 4.6 `core` App *(New in v2.0)*
**Responsibility:** Cross-cutting infrastructure shared by multiple domain apps — avoids duplicating logic across `feed`, `archive`, and `users`.

Contents:
- `core/tasks.py` — the single generic Celery task used for all image
  processing (see §10). One implementation, reused via `apps.get_model()`
  rather than three near-duplicate per-app tasks.
- `core/throttles.py` — shared DRF throttle classes (e.g. `BurstRateThrottle`,
  `SustainedRateThrottle`).
- `core/permissions.py` — shared DRF permission classes (e.g. `HasScope`).
- `core/storage.py` — small wrapper around `django-storages` so app code
  never imports `boto3` directly.

This app has **no models** and **no URLs** — it exists purely to be
imported by the other six apps.

### 4.7 `api` App *(New in v2.0)*
**Responsibility:** The public-facing API gateway. Owns versioning, the
service-account/client model, JWT token endpoints, and the root API
router — but **not** domain business logic, which stays in `archive` and
`linking`.

Models: `APIClient` (new — see §5.10)
Key Views: `token_obtain`, `token_refresh` (wraps SimpleJWT), root DRF
`Router` that includes `archive.viewsets` and `linking.viewsets`
URL Namespace: `/api/v1/`

> **✅ Architect's Note — Why a Separate `api` App Instead of Bolting DRF
> onto Each Domain App's `urls.py`:**
> Versioning (`/api/v1/` → `/api/v2/` someday), auth policy, throttling
> defaults, and OpenAPI schema generation are gateway-level concerns, not
> domain concerns. Centralizing them in one app means a future `/api/v2/`
> can reuse the same `archive`/`linking` serializers with different
> pagination or auth rules, without touching domain code at all.

---

## 5. Database Schema

*Sections 5.1–5.9 are unchanged from v1.1 and reproduced here for
completeness. Changes are called out explicitly where they occur.*

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

*Unchanged.* Avatar processing remains synchronous (Pillow, in-request) —
see the scoping decision in §10. Low volume, low risk; moving it to Celery
would be process for its own sake.

---

### 5.2 `feed_category`

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | |
| `name` | `VARCHAR(100)` | UNIQUE, NOT NULL | e.g., "Food", "Attire", "Rituals" |
| `slug` | `VARCHAR(100)` | UNIQUE, NOT NULL | URL-safe identifier |
| `description` | `TEXT` | NULLABLE | |

*Unchanged.*

---

### 5.3 `feed_hashtag`

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | |
| `name` | `VARCHAR(100)` | UNIQUE, NOT NULL | Stored without `#` |

*Unchanged.*

---

### 5.4 `feed_post`

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | |
| `author_id` | `INTEGER` | FK → `auth_user` | |
| `caption` | `TEXT` | NOT NULL | |
| `image` | `VARCHAR(255)` | NULLABLE | Media path (final, processed) |
| `thumbnail` | `VARCHAR(255)` | NULLABLE | **NEW** — 400×400 crop, generated by Celery |
| `processing_status` | `VARCHAR(20)` | DEFAULT `'pending'` | **NEW** — ENUM: `'pending'`, `'processing'`, `'ready'`, `'failed'` |
| `category_id` | `BIGINT` | FK → `feed_category`, NULLABLE | |
| `geolocation` | `VARCHAR(200)` | NULLABLE | Free-text location string |
| `latitude` | `DECIMAL(9,6)` | NULLABLE | Future map use |
| `longitude` | `DECIMAL(9,6)` | NULLABLE | Future map use |
| `created_at` | `TIMESTAMPTZ` | DEFAULT `NOW()` | |
| `updated_at` | `TIMESTAMPTZ` | AUTO | |
| `is_published` | `BOOLEAN` | DEFAULT `TRUE` | Soft delete mechanism |

**Relationships:**
- `feed_post` ↔ `feed_hashtag`: M2M via `feed_post_hashtags` join table (unchanged)

> **✅ Architect's Note — Migration Safety:**
> `thumbnail` and `processing_status` are **additive** columns — no
> existing column is altered or dropped, and the v1.1 schema's constraints
> are fully preserved. Existing rows backfill `processing_status='ready'`
> in the migration's `RunPython`, since they were already fully processed
> under the v1.1 synchronous pipeline. This migration is zero-downtime.

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
| `processing_status` | `VARCHAR(20)` | DEFAULT `'pending'` | **NEW** — same ENUM as `feed_post`, for `cover_image` |
| `is_verified` | `BOOLEAN` | DEFAULT `FALSE` | Set by Trust Layer |
| `created_at` | `TIMESTAMPTZ` | DEFAULT `NOW()` | |
| `updated_at` | `TIMESTAMPTZ` | AUTO | |

*Same additive-migration note as §5.4 applies.*

---

### 5.6 `archive_recipeschema`

*Unchanged from v1.1.*

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

*Unchanged from v1.1.*

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | |
| `entry_id` | `BIGINT` | FK → `archive_archiveentry`, UNIQUE | One-to-one |
| `steps` | `JSONB` | NOT NULL | `[{"step": 1, "description": "..."}]` |
| `occasions` | `VARCHAR(255)` | NULLABLE | Comma-separated tags |
| `required_items` | `TEXT` | NULLABLE | |

---

### 5.8 `linking_postarchivelink`

*Unchanged from v1.1 — this constraint remains absolutely load-bearing.*

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | |
| `post_id` | `BIGINT` | FK → `feed_post` | |
| `entry_id` | `BIGINT` | FK → `archive_archiveentry` | |
| `suggested_by_id` | `INTEGER` | FK → `auth_user` | Who created the link |
| `is_verified` | `BOOLEAN` | DEFAULT `FALSE` | Griot-verified link |
| `created_at` | `TIMESTAMPTZ` | DEFAULT `NOW()` | |

**Constraint:** `UNIQUE(post_id, entry_id)` — no duplicate links.

> **✅ Architect's Note — Data Integrity (carried over from v1.1):**
> This constraint is intentional and non-negotiable. It now also protects
> against duplicate links created via the public API — a third-party
> integration submitting the same `(post_id, entry_id)` pair twice is
> rejected at the database level exactly like a UI double-submit would be.
> **No new ingestion path gets to bypass this.**

---

### 5.9 `trust_vote`

*Unchanged from v1.1.*

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

### 5.10 `api_apiclient` *(New in v2.0)*

Represents a registered third-party integration partner (a museum, a
research institution, a partner app). Each `APIClient` maps to a Django
`User` acting as a **service account** — JWT auth still authenticates a
`User`; this table adds the integration-specific metadata DRF's permission
classes check against.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | |
| `user_id` | `INTEGER` | FK → `auth_user`, UNIQUE | Service-account user this client authenticates as |
| `name` | `VARCHAR(150)` | NOT NULL | Organization / integration name, shown in admin |
| `is_active` | `BOOLEAN` | DEFAULT `TRUE` | Kill switch — deactivate without deleting history |
| `scopes` | `VARCHAR(255)` | DEFAULT `'read:archive,read:linking'` | Comma-separated scope list (simple scope model, not a full OAuth2 scope registry) |
| `created_at` | `TIMESTAMPTZ` | DEFAULT `NOW()` | |
| `last_used_at` | `TIMESTAMPTZ` | NULLABLE | Updated on each authenticated API request; surfaces dormant/compromised clients |

> **⚠️ Architect's Note — JWT + Scoped Service Accounts vs. Full OAuth2:**
> The brief allows either OAuth2 or JWT rotation. I chose **JWT
> (djangorestframework-simplejwt) with rotation and blacklisting**, paired
> with this lightweight `APIClient` scope model, over a full
> `django-oauth-toolkit` deployment. Full OAuth2's main value —
> a 3-legged, user-delegated consent flow ("Annsana user logs into Partner
> App and grants it access to *their* data") — isn't what's being asked
> for here. What's being asked for is **server-to-server integration**:
> a museum's backend pulling Archive data, not an Annsana user authorizing
> a third-party app on their behalf. A custom token endpoint
> (`POST /api/v1/auth/token/` with `client_id`/`client_secret`) issuing a
> JWT pair scoped to the matching `APIClient` gets us that with far less
> operational surface area than running a full OAuth2 provider.
>
> **Upgrade path:** if Annsana later wants a public "connect your Annsana
> account" integration marketplace — i.e., genuine user-delegated
> authorization — that is the trigger to introduce `django-oauth-toolkit`
> alongside this, not to replace it. The two are not mutually exclusive.

---

### 5.11–5.12 `token_blacklist_outstandingtoken` / `token_blacklist_blacklistedtoken` *(New in v2.0, via `rest_framework_simplejwt.token_blacklist`)*

These two tables are managed entirely by SimpleJWT's `token_blacklist` app
and are not modeled by hand — they're listed here only so the schema
inventory is complete and so nobody is surprised by them in `migrate`
output. `OutstandingToken` records every refresh token issued (for audit
and revocation); `BlacklistedToken` records ones that have been rotated out
or explicitly revoked. A scheduled cleanup (`flushexpiredtokens` management
command) prevents unbounded growth — see §17.

---

## 6. URL & Routing Structure

```
annsana/
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
├── /trust/
│   ├── vote/                   → trust:vote_cast       [HTMX POST, rate-limited]
│   └── status/<target>/        → trust:status_fragment [HTMX GET]
│
└── /api/v1/                                              ← NEW in v2.0
    ├── auth/token/              → api:token_obtain        [client_id + client_secret → JWT pair]
    ├── auth/token/refresh/      → api:token_refresh        [rotates + blacklists old refresh token]
    ├── archive/entries/         → api:archiveentry-list    [GET, public, paginated, filterable]
    ├── archive/entries/<slug>/  → api:archiveentry-detail  [GET, public]
    ├── links/                   → api:postarchivelink-list [GET public; POST requires write:linking scope]
    ├── links/<id>/              → api:postarchivelink-detail [GET, public]
    ├── schema/                  → api:schema               [OpenAPI 3 schema, drf-spectacular]
    └── docs/                    → api:docs                 [Swagger UI]
```

> **✅ Architect's Note — Two Ingress Paths, Deliberately Separate:**
> Everything above the `/api/v1/` block is session-authenticated, HTML-
> returning, and CSRF-protected — exactly as in v1.1. Everything inside
> `/api/v1/` is JWT-authenticated, JSON-returning, and CSRF-exempt (JWT in
> the `Authorization` header is itself the CSRF mitigation — there's no
> ambient browser credential to forge). **These two surfaces must never be
> merged.** A view that accepts both session and JWT auth on the same
> endpoint is exactly how CSRF and scope-bypass bugs get introduced. Keep
> the `api` app's views JWT-only.

---

## 7. API Contracts

### 7.1 Internal HTMX Endpoints *(unchanged from v1.1 — reproduced for completeness)*

These endpoints return HTML fragments, not JSON. They are consumed
exclusively by HTMX attributes in templates and are **not** part of the
public API surface described in §7.2.

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

### 7.2 Public REST API *(New in v2.0)*

JSON-only, versioned at `/api/v1/`, documented via an auto-generated OpenAPI
3 schema (`drf-spectacular`). Pagination uses DRF's `PageNumberPagination`
(default page size 25, max 100) on all list endpoints.

| Endpoint | Method | Auth | Throttle Scope | Notes |
|---|---|---|---|---|
| `/api/v1/auth/token/` | `POST` | None (credentials in body) | `AnonRateThrottle` | `client_id` + `client_secret` → access + refresh JWT pair |
| `/api/v1/auth/token/refresh/` | `POST` | Refresh token | `AnonRateThrottle` | Rotates refresh token; blacklists the old one |
| `/api/v1/archive/entries/` | `GET` | None required | `anon` / `client` (tiered) | List, filterable by `category`, `entry_type` |
| `/api/v1/archive/entries/<slug>/` | `GET` | None required | `anon` / `client` (tiered) | Single entry, includes nested `RecipeSchema`/`GuidelineSchema` if present |
| `/api/v1/links/` | `GET` | None required | `anon` / `client` (tiered) | List, filterable by `post`, `entry`, `is_verified` |
| `/api/v1/links/` | `POST` | JWT, scope `write:linking` | `client-write` (stricter) | Creates a link exactly like the web flow — lands `is_verified=False` |
| `/api/v1/links/<id>/` | `GET` | None required | `anon` / `client` (tiered) | Single link |

**Versioning strategy:** URL path versioning (`/api/v1/...`), not
Accept-header versioning. Path versioning is cache-friendly, proxy-
friendly, and immediately visible in logs and integration partners' code —
worth the minor stylistic cost of the `/v1/` segment.

**Why `Vote` has no endpoint here:** see the Architect's Note in §12.

---

## 8. Authentication & Permissions

### Role Hierarchy *(unchanged)*

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

### Django Permission Strategy *(unchanged)*

- Use Django's built-in `LoginRequiredMixin` for all write operations.
- Create a custom `GriotRequiredMixin` that checks `request.user.userprofile.is_griot`.
- Griot status is set **only by Django admin** at MVP. No self-promotion mechanism.
- All permission failures return an HTMX-aware redirect (check `HX-Request` header to return a `HX-Redirect` response instead of a standard 302).

### Session Security *(unchanged)*

- `SESSION_COOKIE_HTTPONLY = True`
- `SESSION_COOKIE_SECURE = True` (production)
- `CSRF_COOKIE_SECURE = True` (production)
- Django's built-in CSRF protection applies to all HTMX POST requests.

### 8.1 API Authentication (JWT) *(New in v2.0)*

```python
# settings — SimpleJWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # overridden per-view for writes
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '10000/day',
        'client-write': '60/hour',
    },
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
}
```

- **Access tokens:** 15-minute lifetime — short enough that a leaked token
  has a small blast radius.
- **Refresh tokens:** 7-day lifetime, **rotated on every use**, and the
  prior token is **blacklisted** the moment it's rotated out. A stolen
  refresh token is only useful until its next legitimate use — after that,
  reuse is detectable and rejected.
- **Scopes** live on `APIClient.scopes`, checked by a custom
  `core.permissions.HasScope` permission class on write-capable views.

> **✅ Architect's Note — Public Reads, Gated Writes:**
> Given Annsana's mission of cultural preservation and education,
> **read** access to the Archive and Linking data is `AllowAny` by
> default — requiring authentication just to *read* a recipe's history
> would work against the platform's purpose. Authentication is required
> only for (a) write operations and (b) higher-volume programmatic access:
> anonymous reads are capped at 100/day per IP; authenticated `APIClient`
> reads get 10,000/day. This tiered-throttle pattern, not an auth wall, is
> what protects the database from anonymous scraping at scale while
> keeping the data itself genuinely open.

---

## 9. Frontend Architecture

*Unchanged from v1.1.* This revision touches the API and async-processing
layers only — the Tailwind design system, template hierarchy, and HTMX
configuration in the original §9 remain exactly as specified. (See the
existing TSD for the full design-token table and template tree if needed —
not reproduced here since nothing changed.)

---

## 10. File & Media Handling

### Settings

```python
# Default (S3-compatible) in production — see §17 for env-var wiring.
DEFAULT_FILE_STORAGE = 'storages.backends.s3.S3Storage'  # production.py only

ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp']
MAX_UPLOAD_SIZE_MB  = 10
```

> **⚠️ Architect's Note — `[SUPERSEDED]` Original Guidance Against Celery:**
> The v1.1 TSD explicitly said *"Do not introduce a task queue (Celery) for
> this at MVP. It adds operational complexity before it is needed."* That
> was correct **for an MVP serving Annsana's own UI only.** It's no longer
> correct now that uploads can also arrive from third-party integrations
> via the API (§7.2) at volumes and patterns we don't control. The
> operational cost of Celery is now justified by the need to (a) never let
> an integration partner's bulk upload block a request thread, and (b)
> apply the exact same processing pipeline regardless of whether the image
> arrived via the web form or the API. This note replaces, not appends to,
> the original guidance.

### Asynchronous Image Processing (Celery)

**Pipeline, as of v2.0:**

1. View or API serializer receives the upload and saves the model instance
   immediately with `processing_status='pending'` and the raw file in
   place.
2. The save handler enqueues **one generic, reusable Celery task**
   (`core.tasks.process_image_field`) rather than a per-model task:

```python
# apps/core/tasks.py
from celery import shared_task
from django.apps import apps

@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def process_image_field(self, app_label, model_name, object_id, field_name):
    """
    Generic image pipeline: validate → resize → WebP → thumbnail → save.
    Reused by Post.image, ArchiveEntry.cover_image, and any future
    image-bearing model — no per-model duplication.
    """
    Model = apps.get_model(app_label, model_name)
    try:
        instance = Model.objects.get(pk=object_id)
    except Model.DoesNotExist:
        return  # object deleted before the task ran; nothing to do

    instance.processing_status = 'processing'
    instance.save(update_fields=['processing_status'])

    try:
        # Pillow: validate MIME + magic bytes, resize to 1200px longest
        # side, convert to WebP, generate a 400x400 thumbnail, write both
        # to the configured storage backend (local in dev, S3 in prod —
        # the model/view code never knows which).
        ...
        instance.processing_status = 'ready'
    except Exception as exc:
        instance.processing_status = 'failed'
        instance.save(update_fields=['processing_status'])
        raise self.retry(exc=exc)

    instance.save(update_fields=['processing_status', 'image', 'thumbnail'])
```

3. The web view returns immediately with the post/entry showing a
   "processing" placeholder (HTMX polls a small partial every 2s via
   `hx-trigger="every 2s"` until `processing_status` flips to `'ready'`,
   then swaps in the final image). The API returns `202 Accepted` with the
   object's URL for polling.
4. Avatar uploads (`UserProfile.avatar`) **stay synchronous** — see §5.1.
   Low volume, low risk; routing them through Celery would be process for
   its own sake, not a real scaling need.

### Redis: One Instance, Two Roles, Separate Logical DBs

```python
# settings — Celery
CELERY_BROKER_URL = env('REDIS_URL', default='redis://redis:6379/0')
CELERY_RESULT_BACKEND = env('REDIS_URL', default='redis://redis:6379/0')

# settings — Django cache (used by django-ratelimit and DRF throttling)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': env('REDIS_CACHE_URL', default='redis://redis:6379/1'),
    }
}
```

> **⚠️ Architect's Note — Don't Share a Redis Logical DB Between Broker and Cache:**
> Celery's broker needs durability — a task sitting in the queue must
> never be evicted. The Django cache used for rate-limit counters is the
> opposite: it *should* evict under memory pressure (that's what LRU is
> for). Pointing both at Redis logical DB `0` risks the cache's eviction
> policy silently dropping in-flight Celery messages, or a misconfigured
> `maxmemory-policy` starving the queue. Use separate logical DB indices
> (`/0` for broker, `/1` for cache) at minimum; on larger deployments, use
> physically separate Redis instances.

### Archive Entry Images

- Cover images follow the same async pipeline, saved to
  `archive/<year>/<month>/` on the configured storage backend (S3 in
  production — see §17).
- Max dimensions: `1600px` wide (unchanged from v1.1).

---

## 11. The Linking Engine

*Flow and Business Rules below are unchanged from v1.1.* The only addition
is a second ingestion path into the same flow.

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

### Business Rules *(unchanged)*

- A Post can link to **multiple** Archive Entries.
- An Archive Entry can be linked from **multiple** Posts.
- Duplicate `(post_id, entry_id)` pairs are rejected at the DB constraint level.
- Only **Griots** can verify links. Regular users can suggest links.
- A Griot cannot verify their own suggested link.

> **✅ Architect's Note — API Access Does Not Bypass Governance:**
> A scoped `APIClient` calling `POST /api/v1/links/` enters **exactly the
> same flow** as a logged-in user clicking "Link to Archive" — the created
> row still has `is_verified=False`, still requires Griot review, and is
> still subject to the same `UNIQUE(post_id, entry_id)` constraint. There
> is no privileged write path for partners. If a museum's integration is
> trusted enough to skip human review, that is a policy decision for a
> future Griot-tier `APIClient` scope (e.g. `write:linking:verified`) —
> explicitly **not implemented in v2.0** — not something the API layer
> should grant by default.

---

## 12. The Trust Layer (Verification System)

### Reputation Score Logic *(unchanged)*

```
UserProfile.reputation_score =
    SUM of upvotes received on Archive Entries authored by the user
  + SUM of upvotes received on Links suggested by the user
  - SUM of downvotes received on same targets
```

Reputation is recalculated via a Django signal (`post_save` on `Vote`) and cached on the `UserProfile` row for performance.

> **⚠️ Architect's Note — Signals vs. Explicit Logic (carried over from v1.1):**
> Encapsulate the recalculation logic inside `UserProfile.recalculate_reputation()`,
> called by the signal rather than containing the logic itself, so it stays
> unit-testable and manually invocable.

### Griot Promotion (MVP) *(unchanged)*

- Manual: Django superuser sets `userprofile.is_griot = True` via admin.
- Future: Automated promotion when `reputation_score >= GRIOT_THRESHOLD`.

### Verification Threshold *(unchanged)*

```python
ENTRY_VERIFICATION_THRESHOLD = 3
LINK_VERIFICATION_THRESHOLD  = 2
```

### 12.1 Voting Is Not a Public API Surface *(New in v2.0)*

> **⚠️ Architect's Note — Why `Vote` Has No `/api/v1/` Endpoint:**
> This is a deliberate omission, not an oversight. Two reasons:
> 1. **Trust signals need to stay tied to verified human interaction.**
>    Exposing voting over a JWT-authenticated API gives a script the same
>    capability a browser session has, multiplied by however fast an
>    `APIClient` can fire requests. Rate limiting (below) helps, but doesn't
>    fully solve sockpuppet/Sybil-style manipulation — only request-rate
>    abuse. Keeping voting HTMX/session-only is itself a control, not just
>    a missing feature.
> 2. **It wasn't asked for.** The brief scopes public API access to "data
>    from the archive and linking modules" — voting was never in that
>    surface, and adding it would be scope creep against the platform's
>    trust model.
>
> The existing `/trust/vote/` HTMX endpoint still gets the strict
> rate-limiting requested in this revision — implemented via
> `django-ratelimit`, now backed by the same Redis cache (logical DB `1`,
> per §10) so the limit is enforced correctly across multiple Docker
> replicas rather than per-process:
>
> ```python
> # apps/trust/views.py
> from django_ratelimit.decorators import ratelimit
>
> @ratelimit(key='user', rate='20/m', block=True)
> @ratelimit(key='user', rate='200/d', block=True)
> def vote_cast(request):
>     ...
> ```

---

## 13. Non-Functional Requirements

### Performance

| Requirement | Target |
|---|---|
| Feed page initial load (3G) | < 3 seconds |
| HTMX partial response time | < 500ms |
| **API GET p95 latency** | **< 300ms** (paginated, indexed queries only) |
| **Celery task completion (p95)** | **< 5 seconds** from enqueue to `processing_status='ready'` |
| Database query count per page | < 15 (enforced by Django Debug Toolbar in dev) |

**Strategies** *(v1.1 strategies retained, plus)*:
- `select_related` / `prefetch_related` on all feed/archive querysets **and** all DRF serializers (`ArchiveEntrySerializer` must not N+1 on `RecipeSchema`/`GuidelineSchema`).
- DRF list endpoints paginate by default (`PAGE_SIZE = 25`, max `100`) — no unbounded `GET /api/v1/archive/entries/`.
- Celery tasks run with `max_retries=3` and exponential-ish backoff; a permanently failed task leaves `processing_status='failed'` rather than retrying forever.

### Accessibility *(unchanged)*

- All images require `alt` text.
- Tailwind's `focus:ring` utilities applied to all interactive elements.
- Semantic HTML5 used correctly.
- Minimum colour contrast ratio: 4.5:1 (WCAG AA).

### Security

*v1.1 items retained:*
- `DEBUG = False` in production; enforced via `django-environ`.
- `ALLOWED_HOSTS` explicitly set from environment variables.
- File uploads validated server-side (MIME type + magic bytes).
- Django's `SecurityMiddleware` enabled with HSTS, `X-Frame-Options: DENY`.

*New in v2.0:*
- **JWT access tokens expire in 15 minutes; refresh tokens rotate and
  blacklist on use** (§8.1).
- **CORS allowlist is explicit**, never `*` — `django-cors-headers`
  configured with `CORS_ALLOWED_ORIGINS` from environment, per-integration.
- **API scopes enforced per-endpoint** via `core.permissions.HasScope`;
  default `APIClient` scope is read-only.
- **Tiered, Redis-backed throttling**: anonymous IP-based limits are
  strictest; authenticated `APIClient` limits are more generous; write
  endpoints (`POST /api/v1/links/`) get the strictest scope of all
  (`client-write`, 60/hour).
- **Voting remains rate-limited and API-excluded** (§12.1).
- **Secrets are environment-only** — never baked into a Docker image, never
  committed (§17).

---

## 14. Project Directory Structure

```
annsana/                          # Project root
├── manage.py
├── requirements.txt
├── .env.example
├── tailwind.config.js
├── Dockerfile                    # NEW
├── docker-compose.yml            # NEW
├── .dockerignore                 # NEW
│
├── annsana/                      # Django project config package
│   ├── __init__.py                # NEW: imports celery_app (see celery.py)
│   ├── celery.py                  # NEW: Celery app instance, autodiscover_tasks()
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
│
├── apps/
│   ├── users/                    # unchanged
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   └── templates/users/
│   │
│   ├── feed/
│   │   ├── models.py             # Post (+ thumbnail, processing_status)
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   └── templates/feed/
│   │
│   ├── archive/
│   │   ├── models.py             # ArchiveEntry (+ processing_status), RecipeSchema, GuidelineSchema
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   ├── serializers.py        # NEW
│   │   ├── viewsets.py           # NEW
│   │   └── templates/archive/
│   │
│   ├── linking/
│   │   ├── models.py             # PostArchiveLink
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── serializers.py        # NEW
│   │   ├── viewsets.py           # NEW
│   │   └── templates/linking/
│   │
│   ├── trust/
│   │   ├── models.py             # Vote
│   │   ├── views.py              # vote_cast now @ratelimit'd, Redis-backed
│   │   ├── signals.py
│   │   ├── urls.py
│   │   └── templates/trust/
│   │
│   ├── core/                     # NEW — no models, no urls
│   │   ├── tasks.py               # generic process_image_field Celery task
│   │   ├── throttles.py
│   │   ├── permissions.py         # HasScope
│   │   └── storage.py
│   │
│   └── api/                      # NEW — the gateway
│       ├── models.py              # APIClient
│       ├── admin.py
│       ├── views.py               # token_obtain, token_refresh
│       ├── urls.py                # root /api/v1/ router
│       └── migrations/
│
├── templates/                    # unchanged
│   ├── base.html
│   ├── components/
│   └── partials/
│
├── static/                       # unchanged
│   ├── css/
│   └── js/
│
└── media/                        # dev only; gitignored — prod uses S3 (see §17)
```

---

## 15. MVP Scope & Out-of-Scope

### ✅ In Scope (v1.1 MVP — unchanged)

- User registration, login, logout
- User profile page
- Post creation with text caption and single image upload
- Category and hashtag tagging on posts
- Feed home page (chronological, paginated via HTMX infinite scroll)
- Archive Entry creation (Title, Body, Category) — Griot only
- Archive Entry detail page
- Post → Archive Entry link creation and display
- Upvote/downvote on Archive Entries and Links
- Reputation score display on user profile
- Django admin for all models
- Basic `is_griot` flag and Griot-only view guards

### ✅ In Scope (v2.0 additions)

- Public, versioned, read-mostly REST API for Archive and Linking data
- JWT authentication with rotation + blacklisting; scoped `APIClient` model
- Asynchronous image processing pipeline (Celery + Redis)
- **S3-compatible media storage** *(moved here from Out-of-Scope below)*
- Docker / Docker Compose deployment configuration
- Redis-backed, tiered rate limiting on both the API and the existing
  voting endpoint

### ❌ Out of Scope (Post-MVP / Post-v2.0)

- Video upload and playback
- Comments on posts or archive entries
- Direct messaging
- Geolocation map view
- Recipe/Guideline schema forms (schema models exist; UI forms deferred)
- Automated Griot promotion
- Email notifications
- Full-text search (PostgreSQL `tsvector`)
- Social follow system
- Content moderation / reporting tools
- Mobile app (React Native)
- **Voting/verification exposed via the public API** *(deliberate exclusion — §12.1, not a deferral)*
- **Full OAuth2 / user-delegated consent flow** *(upgrade path noted in §5.10; not needed for v2.0's server-to-server integration use case)*
- Celery Beat scheduled jobs (only an ad-hoc `flushexpiredtokens` cron is in scope — see §17)
- Kubernetes / multi-region orchestration (Docker Compose covers staging parity only; production orchestration is a future decision)

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
| **Phase 7** *(New)* | **Integration & Scale** | `core` + `api` apps; DRF + JWT + `APIClient`; Celery + Redis async image pipeline; `processing_status` migrations; Docker Compose; S3 storage cutover |

Each phase produces a working, testable vertical slice of the application
before the next phase begins. Phase 7 depends on Phases 2–5 being complete,
since it exposes and extends their models rather than introducing new
domain concepts.

---

## 17. Deployment Architecture (Docker)

### Services

```yaml
# docker-compose.yml (development / staging parity — see note below for production)
services:
  web:
    build: .
    command: gunicorn annsana.wsgi:application --bind 0.0.0.0:8000
    env_file: .env
    depends_on: [db, redis]
    ports: ["8000:8000"]

  worker:
    build: .
    command: celery -A annsana worker --loglevel=info
    env_file: .env
    depends_on: [redis, db]

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: annsana
      POSTGRES_USER: annsana
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes: ["pgdata:/var/lib/postgresql/data"]

  redis:
    image: redis:7

volumes:
  pgdata:
```

> **⚠️ Architect's Note — `db` and `redis` Containers Are for Dev/Staging
> Parity Only:**
> In production, `db` should be a managed Postgres service (RDS, Cloud SQL,
> etc.) and `redis` a managed Redis service (ElastiCache, Upstash, etc.) —
> **not** same-host containers. Running a stateful database in a container
> alongside your stateless app containers throws away the durability,
> backup, and failover guarantees a managed service gives you for a
> relatively small cost saving. `docker-compose.yml` as shown is correct
> for local development and CI; production `docker-compose.prod.yml` (or
> your orchestrator's manifest) should point `DATABASE_URL` and `REDIS_URL`
> at managed endpoints instead of the `db`/`redis` service names.

### Dockerfile (multi-stage)

```dockerfile
# --- Stage 1: build Tailwind CSS ---
FROM node:20-slim AS frontend-builder
WORKDIR /app
COPY package.json tailwind.config.js ./
COPY static/css/input.css ./static/css/input.css
COPY templates ./templates
COPY apps ./apps
RUN npm install && npm run build:css

# --- Stage 2: Python runtime ---
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
COPY --from=frontend-builder /app/static/css/output.css ./static/css/output.css
RUN python manage.py collectstatic --noinput --settings=annsana.settings.production
CMD ["gunicorn", "annsana.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### `.dockerignore`

```
.env
.git
media/
node_modules/
__pycache__/
*.pyc
db.sqlite3
```

### Secrets & Configuration

- All secrets (`SECRET_KEY`, `DATABASE_URL`, `REDIS_URL`,
  `AWS_SECRET_ACCESS_KEY`, JWT signing material) are injected as
  **container environment variables** at deploy time — via Docker secrets,
  an orchestrator's secret store, or the hosting platform's env-var
  injection. **None are baked into the image**, and `.env` is excluded by
  `.dockerignore` so it can never accidentally end up in a build context.
- `django-environ` (already in the stack since v1.1) reads these
  identically whether they come from a local `.env` file or injected
  container env vars — no code change needed between environments.

### S3-Compatible Storage Configuration

```python
# production.py
STORAGES = {
    'default': {
        'BACKEND': 'storages.backends.s3.S3Storage',
        'OPTIONS': {
            'bucket_name': env('AWS_STORAGE_BUCKET_NAME'),
            'endpoint_url': env('AWS_S3_ENDPOINT_URL', default=None),  # set for R2; omit for AWS S3
            'access_key': env('AWS_ACCESS_KEY_ID'),
            'secret_key': env('AWS_SECRET_ACCESS_KEY'),
            'default_acl': 'public-read',
            'querystring_auth': False,
        },
    },
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}
```

This directly replaces the `media/` filesystem volume in production. Local
development is unaffected — `development.py` still uses
`FileSystemStorage` against the local `media/` directory, so contributors
don't need real S3 credentials to run the app locally.

### Scheduled Maintenance

A single cron-style job (run via the orchestrator's scheduler, or a
`worker` container running `celery -A annsana beat` if Celery Beat is
introduced later) should periodically run:

```bash
python manage.py flushexpiredtokens
```

to purge expired entries from `token_blacklist_outstandingtoken` /
`token_blacklist_blacklistedtoken`, preventing unbounded growth. This is
the one piece of "scheduled task" infrastructure in scope for v2.0 — full
Celery Beat adoption is deferred until a second scheduled-task need
actually materializes (§15).

---

*This document is the authoritative technical reference for Annsana
development from v2.0 onward. All subsequent module builds must conform to
the schemas, naming conventions, and architectural decisions defined
herein — including those carried forward unchanged from v1.1.*
