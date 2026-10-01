---
kind: external_dependency
name: Cloudflare — CDN / reverse proxy in front of Nginx
slug: cloudflare
category: external_dependency
category_hints:
    - client_constraint
scope:
    - '**'
---

Cloudflare sits in front of the Nginx+Gunicorn stack (CLAUDE.md §1). Two concrete integration consequences:
- Cache bypass or `Vary: HX-Request` must be configured so Cloudflare does not serve an HTMX fragment as a full page.
- Email addresses on the live site are hidden behind Cloudflare's email obfuscation (`data-cfemail` attributes), which is why the Phase 0 extraction script had to parse saved HTML rather than relying on DOM text.