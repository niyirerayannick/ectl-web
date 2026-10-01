---
kind: logging_system
name: Django Logging — Console Handler in Development Only
category: logging_system
scope:
    - '**'
source_files:
    - config/settings/dev.py
    - config/settings/base.py
---

## What system/approach is used

The project uses **Python's standard library `logging` module** configured through Django's `LOGGING` setting dictionary. No third-party logging framework (structlog, loguru, django-extensions' logging) is installed or referenced.

There is no application-level logger initialization anywhere in the codebase: a grep for `import logging`, `from logging`, `logger =`, and `logging.getLogger` across all `.py` files returns only the single `LOGGING = { ... }` block in `config/settings/dev.py`. None of the Django apps under `apps/` import or use the logging module.

## Key files and packages

- `config/settings/base.py` — base settings; contains **no** `LOGGING` configuration.
- `config/settings/dev.py` — development settings; defines the only `LOGGING` dict in the repo.
- `config/settings/prod.py` — production settings; inherits from `base.py` via `from .base import *` and does not define its own `LOGGING`, so production runs with Django's default logging (which routes to stderr).

## Architecture and conventions

- The logging configuration lives exclusively in the development settings file (`config/settings/dev.py`). Production has no explicit logging config, relying on Django defaults.
- The dev configuration declares:
  - `version: 1`
  - `disable_existing_loggers: False`
  - One handler: `console` using `logging.StreamHandler` (stdout/stderr)
  - A `root` logger attached to the console handler at level `WARNING`
- There are no per-app loggers, no formatters, no file handlers, no structured fields, no request-correlation IDs, and no log rotation.
- Because no app code imports `logging`, there is no convention for how log messages should be emitted — the logging subsystem is effectively unpopulated beyond the root handler.

## Conventions and constraints

- **Observed pattern**: Logging configuration is environment-scoped to `dev.py`; `prod.py` intentionally omits it so production falls back to Django defaults.
- **No enforcement mechanism**: There is no lint rule, test, or shared base that enforces usage of a particular logger name or message format. The absence of any `logging` imports in `apps/` means the current convention is simply "no application logging yet".
- The `LOGGING` dict in `dev.py` sets the root logger to `WARNING`, which suppresses INFO/DEBUG output from Django itself unless a more specific logger is configured later.