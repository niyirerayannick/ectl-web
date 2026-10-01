# Energicotel (ECTL) PLC — website

Django 5.2 + Tailwind CSS v4 + HTMX 2 + Alpine.js 3 rebuild of
<https://www.energicotel.com> (WordPress migration).

The full specification — sitemap, design tokens, page analysis, phase plan —
lives in [`CLAUDE.md`](CLAUDE.md). **Current state: Phase 1 (scaffold).**
No pages are built yet; page work starts in Phase 2.

## Stack

| Layer | Choice |
| --- | --- |
| Backend | Django 5.2 LTS, Python 3.12+ |
| Database | PostgreSQL via `DATABASE_URL`; SQLite fallback (`var/db.sqlite3`) in dev |
| CSS | Tailwind CSS v4 via django-tailwind-cli (standalone CLI — no Node.js), CSS-first `@theme` config |
| Interactivity | HTMX 2 (django-htmx) + Alpine.js 3 — progressive enhancement, pages work without JS |
| Templates | Django templates + django-template-partials |
| Admin | django-unfold |
| Static files | WhiteNoise |
| Tests | pytest + pytest-django |

## Layout

```
config/            settings/ (base, dev, prod), urls.py, wsgi.py
apps/              core, team, units, news, gallery, contact
templates/         base.html + per-app page templates (built from Phase 2)
theme/static_src/src/styles.css    Tailwind v4 entry — the @theme token block (Phase 2)
static/            js/app.js + vendored js/vendor/{htmx,alpine}.min.js
requirements/      base / dev / prod
design_reference/  Phase 0 extraction output (tokens.json, screenshots) — committed
```

## Development setup

Requires Python 3.12+.

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements\dev.txt
copy .env.example .env        # optional — every value has a dev default

python manage.py migrate        # creates var/db.sqlite3 (SQLite fallback)
python manage.py tailwind build # downloads the Tailwind CLI on first run,
                                # then compiles theme/static_src/src/styles.css
```

> Note: WhiteNoise prints a one-time `No directory at: staticfiles\` warning
> on a fresh clone until the first `collectstatic` run — harmless in development.

## Run

```powershell
python manage.py runserver          # http://127.0.0.1:8000/
python manage.py tailwind watch     # separate terminal: rebuild CSS on change
```

Admin UI (django-unfold): <http://127.0.0.1:8000/admin/> —
create an admin user with `python manage.py createsuperuser`.

## Tests

```powershell
pytest
```

## Production

Set `DJANGO_SETTINGS_MODULE=config.settings.prod` with `SECRET_KEY`,
`ALLOWED_HOSTS`, `DATABASE_URL` (PostgreSQL) and `CSRF_TRUSTED_ORIGINS`
(see `.env.example`), then:

```powershell
python manage.py tailwind build
python manage.py collectstatic --noinput
gunicorn config.wsgi:application
```

Gunicorn sits behind Nginx; Cloudflare stays in front (CLAUDE.md §1).

## Vendored JavaScript

`static/js/vendor/` holds pinned copies of the front-end libraries so the site
is fully self-hosted:

- `htmx.min.js` — htmx.org 2.0.11
- `alpine.min.js` — alpinejs 3.17.4 (CDN build)

To upgrade, download the desired version from
<https://cdn.jsdelivr.net/npm/htmx.org/> and
<https://cdn.jsdelivr.net/npm/alpinejs/> and update the versions listed here.
