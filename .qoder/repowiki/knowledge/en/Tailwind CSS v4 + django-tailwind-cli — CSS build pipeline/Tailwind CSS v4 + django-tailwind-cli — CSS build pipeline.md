---
kind: external_dependency
name: Tailwind CSS v4 + django-tailwind-cli — CSS build pipeline
slug: tailwind-css-v4
category: external_dependency
category_hints:
    - framework_behavior
scope:
    - '**'
---


Key integration facts:
- `{% tailwind_css %}` template tag renders a `<link>` via `{% static %}` (manifest-aware in prod).
- `TAILWIND_CLI_DIST_CSS` path is relative to the first `STATICFILES_DIRS` entry.
- The CLI binary is downloaded into `BASE_DIR/.django_tailwind_cli/` (gitignored).
- `@source` paths resolve relative to the stylesheet file, not the working directory.
- Build/watch commands: `python manage.py tailwind build` / `watch`.
- Pinning note: the conversation pinned the resolved CLI version (v4.3.3) for reproducible builds.