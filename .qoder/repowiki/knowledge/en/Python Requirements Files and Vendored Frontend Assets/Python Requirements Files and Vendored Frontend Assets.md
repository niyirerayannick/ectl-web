---
kind: dependency_management
name: Python Requirements Files and Vendored Frontend Assets
category: dependency_management
scope:
    - '**'
source_files:
    - requirements/base.txt
    - requirements/dev.txt
    - requirements/prod.txt
    - static/js/vendor/htmxt.min.js
    - static/js/vendor/alpine.min.js
    - .django_tailwind_cli/tailwindcss-windows-x64-4.3.3.exe
---

## Dependency Management Approach

This Django project uses two complementary strategies for third-party dependencies:

### Python Dependencies — PIP with Environment-Split `requirements/*.txt`

The project declares Python packages exclusively through pip-style requirements files under `requirements/`, organized by environment:

- `requirements/base.txt` — runtime-only dependencies shared by development and production. It pins exact versions (e.g. `Django==5.2.17`, `django-htmx==1.29.0`, `whitenoise==6.12.0`).
- `requirements/dev.txt` — includes base via `-r base.txt` and adds test tooling (`pytest==9.1.1`, `pytest-django==4.14.0`).
- `requirements/prod.txt` — includes base via `-r base.txt` and adds server/runtime extras (`gunicorn>=23.0`, `psycopg[binary]>=3.2,<4`).

There is no `pyproject.toml`, no `setup.py`, no `Pipfile`, and no lockfile (no `requirements.txt` at the repo root, no `poetry.lock`, no `pip-tools` generated file). The three files under `requirements/` are the sole source of truth.

No private PyPI registry or `PIP_INDEX_URL` configuration is present in the repository; dependencies are resolved from the default PyPI index.

### Frontend Dependencies — Manual Vendor Files

Frontend libraries are not managed by npm/pnpm/yarn. Instead, minified JS bundles are checked in directly:

- `static/js/vendor/htmxt.min.js` — HTMX library
- `static/js/vendor/alpine.min.js` — Alpine.js library

These are static assets committed to the repo rather than installed via a package manager. There is no `package.json` anywhere in the tree.

### Tailwind CSS — Bundled CLI Executable

Tailwind is integrated via `django-tailwind-cli` (declared in `base.txt`). The actual Tailwind binary is vendored as a Windows executable:

- `.django_tailwind_cli/tailwindcss-windows-x64-4.3.3.exe`

The version is embedded in the filename, so updating Tailwind requires replacing this file manually alongside the `django-tailwind-cli` Python package version.

## Key Files

- `requirements/base.txt` — pinned runtime dependencies
- `requirements/dev.txt` — dev/test overrides (includes base)
- `requirements/prod.txt` — production server/database overrides (includes base)
- `static/js/vendor/htmxt.min.js` — vendored HTMX
- `static/js/vendor/alpine.min.js` — vendored Alpine.js
- `.django_tailwind_cli/tailwindcss-windows-x64-4.3.3.exe` — vendored Tailwind CLI

## Conventions and Constraints

- **Exact pinning for core runtime deps**: `base.txt` pins every dependency to an exact version using `==` (e.g. `Django==5.2.17`), while prod-only extras use range constraints (`gunicorn>=23.0`, `psycopg[binary]>=3.2,<4`) to allow compatible updates.
- **Environment split via include directives**: `dev.txt` and `prod.txt` both start with `-r base.txt` to compose on top of the shared runtime set; new runtime dependencies belong in `base.txt`, not duplicated in env-specific files.
- **No lockfile**: there is no mechanism to freeze transitive resolution beyond what `pip install -r` does; reproducibility relies on the exact `==` pins in `base.txt`.
- **Frontend libs are vendored, not fetched at build time**: `htmxt.min.js` and `alpine.min.js` are committed into `static/js/vendor/`; they are not downloaded by a build step.
- **Tailwind CLI is platform-bundled**: the Tailwind executable is shipped per-platform (Windows binary in `.django_tailwind_cli/`); the version is part of the filename and must be updated manually when upgrading.