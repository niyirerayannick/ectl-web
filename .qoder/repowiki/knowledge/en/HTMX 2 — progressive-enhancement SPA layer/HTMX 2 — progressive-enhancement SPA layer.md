---
kind: external_dependency
name: HTMX 2 — progressive-enhancement SPA layer
slug: htmx
category: external_dependency
category_hints:
    - framework_behavior
scope:
    - '**'
---


Stable integration rules (from CLAUDE.md §7): partial responses wrap content in `{% partialdef main %}` when `request.htmx` is true and not a history restore; every response adds `Vary: HX-Request` so Cloudflare/browsers never serve a fragment as a full page; sliders/counters/lightbox re-initialise on `htmx.onLoad`; active nav toggles `aria-current="page"` on `htmx:afterSettle`; forms use `hx-post` returning 200 with inline errors rather than 4xx.