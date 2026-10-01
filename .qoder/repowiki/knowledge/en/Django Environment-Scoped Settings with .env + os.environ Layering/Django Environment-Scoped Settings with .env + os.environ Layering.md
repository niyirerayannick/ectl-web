---
kind: configuration_system
name: Django Environment-Scoped Settings with .env + os.environ Layering
category: configuration_system
scope:
    - '**'
source_files:
    - config/settings/base.py
    - config/settings/dev.py
    - config/settings/prod.py
    - .env.example
    - config/wsgi.py
---

## Approach

The project uses Django's built-in multi-module settings pattern (`config/settings/base.py` → `dev.py` / `prod.py`) layered on top of `python-dotenv` and `os.environ`. Secrets and runtime values are loaded from a `.env` file (git-ignored) via `load_dotenv`, then overridden by real environment variables — which always win, as documented in the base module comment.

Database URLs are parsed through `dj_database_url`, allowing PostgreSQL in production and an SQLite fallback in development when `DATABASE_URL` is unset.

## Key Files

- `config/settings/base.py` — shared defaults for every environment; loads `.env`; defines `INSTALLED_APPS`, `MIDDLEWARE`, `TEMPLATES`, static/Tailwind config, database fallback, time zone (`Africa/Kigali`).
- `config/settings/dev.py` — imports `base` via `from .base import *`; sets `DEBUG = True`, whitenoise finders, console email backend, logging to console at WARNING level, and appends localhost/127.0.0.1 to `ALLOWED_HOSTS`.
- `config/settings/prod.py` — hardens defaults: requires `SECRET_KEY`, `DATABASE_URL`, and `ALLOWED_HOSTS` via `django.core.exceptions.ImproperlyConfigured`; enables SSL redirect, HSTS (30 days, preload, subdomains), secure cookies; adds connection pooling (`CONN_MAX_AGE=600`, `CONN_HEALTH_CHECKS=True`).
- `config/wsgi.py` — selects `prod` settings (see its docstring).
- `.env.example` — documents required env vars (`SECRET_KEY`, `ALLOWED_HOSTS`, `DATABASE_URL`, `CSRF_TRUSTED_ORIGINS`) and includes a one-liner to generate `SECRET_KEY`.
- `requirements/base.txt` / `requirements/dev.txt` / `requirements/prod.txt` — dependency manifests split per environment.

## Architecture & Conventions

1. **Three-tier settings inheritance**: `base.py` holds all cross-cutting defaults; `dev.py` and `prod.py` use `from .base import *` and selectively override. This is the standard Django convention and is the only mechanism used here.
2. **Environment variable precedence**: `load_dotenv(BASE_DIR / ".env")` runs first, then `os.environ.get(...)` reads real env vars — so process-level env always overrides `.env`. The base module explicitly states this ordering.
3. **Secrets never live in code**: `SECRET_KEY` falls back to a placeholder string in `base.py` but `prod.py` raises `ImproperlyConfigured` if it is absent. All other secrets follow the same `os.environ.get` pattern.
4. **Database abstraction**: `DATABASE_URL` drives the engine via `dj_database_url.parse`; without it, SQLite under `var/db.sqlite3` is used automatically — no manual setting needed in dev.
5. **Static assets**: WhiteNoise serves them; `STORAGES.staticfiles` is swapped between `CompressedManifestStaticFilesStorage` (prod) and plain `StaticFilesStorage` (dev). Tailwind v4 is configured via `django-tailwind-cli` with a pinned version (`TAILWIND_CLI_VERSION = "4.3.3"`) and a vendored binary under `.django_tailwind_cli/`.
6. **Design tokens separation**: The base settings deliberately exclude design values (colours, fonts, spacing); those live in `theme/static_src/src/styles.css` and will be populated from `design_reference/tokens.json` in Phase 2, per the `CLAUDE.md` comments.
7. **Template context**: A custom `apps.core.context_processors.site` processor exposes site-wide contact info; the comment notes it will be replaced by a `SiteSettings` singleton model in Phase 3.
8. **Middleware ordering is explicit**: Comments document that `SecurityMiddleware` must precede `WhiteNoiseMiddleware`, and `django_htmx.middleware.HtmxMiddleware` is added last to expose `request.htmx`.
9. **Timezone**: Hardcoded to `Africa/Kigali` in `base.py`.

## Conventions & Enforced Rules

- **Rule**: Production startup fails fast if `SECRET_KEY`, `DATABASE_URL`, or `ALLOWED_HOSTS` are missing — enforced by `raise ImproperlyConfigured(...)` in `config/settings/prod.py`.
- **Rule**: `ALLOWED_HOSTS` is parsed as a comma-separated list from `os.environ` (split on `,` and stripped), so multiple hosts are supported via a single env var.
- **Rule**: `CSRF_TRUSTED_ORIGINS` follows the same comma-separated parsing pattern in `prod.py`.
- **Rule**: Development settings are selected by default for `manage.py` (as stated in `dev.py`'s docstring); WSGI selects `prod` (as stated in `prod.py`'s docstring).
- **Convention**: Environment-specific files inherit everything from `base.py` via wildcard import (`from .base import *`) rather than importing individual symbols.
- **Convention**: Database URL is the single source of truth for DB configuration; there is no per-environment `ENGINE`/`NAME` block outside the SQLite fallback path.
- **Convention**: Dependencies are split into `requirements/base.txt`, `requirements/dev.txt`, and `requirements/prod.txt`, mirroring the settings layout.
- **Constraint**: Design tokens (colors, fonts, spacing) are explicitly excluded from Django settings and kept in Tailwind's `@theme` block, as documented in the `base.py` module docstring.