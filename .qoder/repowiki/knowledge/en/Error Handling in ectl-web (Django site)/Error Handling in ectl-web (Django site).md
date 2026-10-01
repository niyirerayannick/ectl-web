---
kind: error_handling
name: Error Handling in ectl-web (Django site)
category: error_handling
scope:
    - '**'
source_files:
    - config/settings/base.py
    - apps/core/views.py
    - apps/contact/views.py
    - templates/base.html
    - extract_design_tokens.py
    - resume_extract.py
---

## What system/approach is used

The repository does not define a custom error-handling framework. Error handling is the default Django stack:

- **Runtime exceptions** propagate through Django's middleware chain and are rendered by Django's built-in debug/production error pages.
- **No custom exception classes** are defined anywhere in `apps/` or `config/` — grep for `class \w+Error|class \w+Exception` returns zero matches across the codebase.
- **No sentinel errors**, no domain-specific error types, and no centralized error-response serializer.
- **Logging**: there is no structured logging setup; the only `logging` usage is absent from application code. The utility scripts (`extract_design_tokens.py`, `resume_extract.py`) swallow broad `Exception`s with `# noqa: BLE001` comments to keep processing going and report at the end.
- **HTMX integration**: `django_htmx.middleware.HtmxMiddleware` is registered in `MIDDLEWARE` so views can inspect `request.htmx`; this is for feature detection, not error handling.
- **Static file serving**: WhiteNoise (`whitenoise.middleware.WhiteNoiseMiddleware`) handles missing static files rather than raising 404s into Django.

## Key files and packages

- `config/settings/base.py` — defines the full `MIDDLEWARE` list and `DEBUG = False`. No `handler404` / `handler500` / `handler403` overrides are present in `config/urls.py` or elsewhere.
- `apps/core/views.py` — only a `TemplateView` scaffold; no try/except blocks.
- `apps/contact/views.py` — currently empty aside from a docstring referencing "inline errors" for Phase 4–5 contact form; no implementation yet.
- `templates/base.html` — base template; no `{% if messages %}` block or error rendering logic.
- `extract_design_tokens.py` — uses `try/except Exception as e:` around image parsing with `# noqa: BLE001` to continue on failure.
- `resume_extract.py` — similar pattern: broad `except OSError` and `except Exception as e: # noqa: BLE001` to tolerate bad inputs during resume extraction.

## Architecture and conventions

Observed patterns (descriptive):

1. **Views are thin**. All business logic lives in models; views are mostly `TemplateView` subclasses. There is no view-level error propagation because there is no complex request flow yet.
2. **No custom exceptions**. Domain errors (e.g., validation failures) are expected to be surfaced via Django forms/messages rather than raised exceptions — consistent with the contact view docstring mentioning "inline errors, success message".
3. **Utility scripts tolerate failures**. The two top-level Python scripts that process design assets use broad `except Exception` with explicit `noqa: BLE001` annotations, indicating an intentional convention of "fail open" for non-critical data extraction tasks.
4. **Debugging vs production behavior** is controlled solely by `DEBUG` in settings (`False` in base, overridden to `True` in `dev.py`). No custom error handlers are wired up.
5. **HTMX-aware responses** will likely be handled at the view level using `request.htmx` (enabled by `HtmxMiddleware`), but no such logic exists yet.

## Conventions and constraints

- **No custom error hierarchy**: grep confirms zero user-defined exception classes in the project.
- **No HTTP handler overrides**: `config/urls.py` does not define `handler404`, `handler500`, or `handler403`; Django defaults apply.
- **No global exception middleware**: the `MIDDLEWARE` list contains only Django core, WhiteNoise, and `django_htmx` — no custom middleware for error aggregation or reporting.
- **Broad exception swallowing is annotated**: every `except Exception` in the repo carries a `# noqa: BLE001` comment (in `resume_extract.py` and `extract_design_tokens.py`), marking it as intentional rather than accidental.
- **Contact form errors are planned as inline/template-level**: the `apps/contact/views.py` docstring states "form with hx-post, inline errors, success message", implying future form validation errors will be rendered in the template rather than raised as exceptions.