---
kind: build_system
name: Build System — Django + Tailwind v4 CLI, pytest, and environment-scoped requirements
category: build_system
scope:
    - '**'
source_files:
    - requirements/base.txt
    - requirements/dev.txt
    - requirements/prod.txt
    - pytest.ini
    - theme/static_src/src/styles.css
    - config/settings/base.py
    - CLAUDE.md
---

## What system/approach is used

The project has no Makefile, Dockerfile, CI pipeline, or release script. Build and packaging are driven by three lightweight mechanisms:

1. **Python dependency management** via `requirements/base.txt`, `requirements/dev.txt`, `requirements/prod.txt` (pip-style `-r base.txt` includes).
2. **Tailwind CSS v4 build** via `django-tailwind-cli` (no Node.js), invoked as `python manage.py tailwind build`; the compiled CSS lands in `theme/static_src/dist/`.
3. **Test runner** configured by `pytest.ini` pointing at `config.settings.dev`.

There is no container image, no CI YAML, no version-bump/release automation committed to the repo. The production stack described in `CLAUDE.md` (Gunicorn behind Nginx, PostgreSQL) is a deployment target, not an implemented build artifact.

## Key files and packages

- `requirements/base.txt` — shared runtime deps: Django 5.2.17, dj-database-url, django-htmx, django-tailwind-cli 4.8.1, django-template-partials, django-unfold, python-dotenv, whitenoise.
- `requirements/dev.txt` — extends base with pytest 9.1.1 and pytest-django 4.14.0.
- `requirements/prod.txt` — extends base with gunicorn >=23.0 and psycopg[binary] >=3.2,<4.
- `pytest.ini` — sets `DJANGO_SETTINGS_MODULE = config.settings.dev`, file patterns, and `addopts = -ra --strict-markers`.
- `theme/static_src/src/styles.css` — Tailwind v4 entry point; built by `python manage.py tailwind build`, output path documented in its header comment.
- `config/settings/base.py` — registers `django_tailwind_cli` in `INSTALLED_APPS`, configures WhiteNoise static handling, and documents the Tailwind CLI integration (cached standalone binary under `.django_tailwind_cli/`).
- `CLAUDE.md` §1–§9 — the authoritative spec for the tech stack, phases, and run commands (e.g. Phase 1 "Done when: `runserver` works, `tailwind` builds, tests pass").

## Architecture and conventions

### Requirements layering
`dev.txt` and `prod.txt` both start with `-r base.txt`. Base holds runtime-only dependencies; dev adds testing tooling; prod adds server/runtime extras (gunicorn, psycopg). This is enforced by the pip include directive — nothing in dev or prod can override base without explicitly re-listing it.

### Tailwind CSS v4 via django-tailwind-cli
- No Node.js or npm is used. The vendored binary lives at `.django_tailwind_cli/tailwindcss-windows-x64-4.3.3.exe` (the platform-specific executable downloaded once and cached).
- Source of truth for design tokens is `theme/static_src/src/styles.css` inside a single `@theme` block. Templates must use token utilities (`bg-brand-primary`, `text-heading`, …) rather than arbitrary values — this is a convention stated in `CLAUDE.md` §0 rule 3 and §5.
- Content scan paths are declared explicitly in the CSS file: `@source "../../../templates"` plus exclusions for `design_reference` and `static/js/vendor` so reference material does not pollute the generated stylesheet.
- Build command: `python manage.py tailwind build` (documented in the CSS file header and in `CLAUDE.md` §1 Phase 1 done criteria).
- Output: `theme/static_src/dist/css/styles.css`, served through WhiteNoise as `/static/css/styles.css` via `{% tailwind_css %}` in `templates/base.html`.

### Static assets
WhiteNoise serves static files directly from Django's `STATICFILES_DIRS` / `collectstatic` layout. There is no separate frontend bundler beyond the Tailwind build step.

### Tests
- pytest is the test runner, configured in `pytest.ini` to use the `dev` settings module.
- Test discovery pattern: `tests.py`, `test_*.py`, `*_tests.py`.
- Strict markers enabled (`--strict-markers`) — any marker used on a test must be declared, otherwise pytest fails.
- A scaffold test in `apps/core/tests/test_scaffold.py` asserts that the expected installed apps list contains `unfold`, `django_htmx`, `template_partials`, `django_tailwind_cli`, acting as a minimal sanity check for the dependency configuration.

### Settings split
Environment-specific settings live under `config/settings/`: `base.py` (shared), `dev.py`, `prod.py`. The `DJANGO_SETTINGS_MODULE` is set per-environment (pytest forces `dev`).

## Conventions and constraints

- **No Node.js**: Tailwind v4 is built exclusively through `django-tailwind-cli`'s vendored binary; there is no `package.json`, `node_modules`, or npm script in the repository.
- **Design values centralized**: All colours, fonts, type scale, radii, shadows, breakpoints, and container width go into the `@theme` block in `theme/static_src/src/styles.css`. Template authors use Tailwind token utilities derived from those variables — arbitrary hex values in templates are prohibited by the CLAUDE.md ground rules (§0 rule 3, §5).
- **Breakpoints match Elementor defaults**: `--breakpoint-md: 768px` and `--breakpoint-lg: 1025px` mirror the source WordPress site's tablet/mobile thresholds (stated in `styles.css` and `CLAUDE.md` §5).
- **Requirements are pinned for runtime**: `Django==5.2.17`, `django-tailwind-cli==4.8.1`, etc. are exact pins in `base.txt`; only dev/prod extras use ranges (`gunicorn>=23.0`, `psycopg[binary]>=3.2,<4`).
- **Tests require pytest-django**: the presence of `pytest-django` in `dev.txt` and the `DJANGO_SETTINGS_MODULE` setting in `pytest.ini` means running tests requires the Django project to be importable against the `dev` settings.
- **No CI / Dockerfile / Makefile**: these artifacts do not exist in the repository. Deployment steps (Gunicorn, Nginx, Dockerfile) are listed as future work in `CLAUDE.md` §7 but are not yet implemented.
- **Phase-gated development**: `CLAUDE.md` §9 defines phases where each phase's completion criteria include running `python manage.py check --deploy` and comparing screenshots at 1440/768/390 px widths — these are the de facto validation gates for the build.