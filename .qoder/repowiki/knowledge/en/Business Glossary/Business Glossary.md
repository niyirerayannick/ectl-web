---
kind: business_term
name: Business Glossary
category: business_term
scope:
    - '**'
---

### ECTL
- Definition：Energicotel PLC, a Rwanda Stock Exchange-listed energy company based in Kigali. The project is a Django/Tailwind/HTMX rebuild of its WordPress site (energicotel.com).
- Aliases：Energicotel、Energicotel PLC

### Phase 0–7
- Definition：The staged migration plan defined in CLAUDE.md §9. Phase 0 = design reference extraction; Phase 1 = Django scaffold; Phase 2 = design tokens + base layout; Phase 3 = models/admin/seed data; Phase 4 = pages; Phase 5 = HTMX SPA layer; Phase 6 = SEO/redirects/security; Phase 7 = performance & deploy. Each phase has explicit done-criteria.
- Aliases：phases、migration phases

### design_reference/tokens.json
- Definition：Structured design-token output produced by `extract_design_tokens.py` from the live WordPress site. Contains per-page element styles (colours, fonts, sizes), breakpoints, and contact data; consumed by Claude Code to fill the `@theme` block in `theme/static_src/src/styles.css` without inventing values.
- Aliases：tokens.json、design tokens

### import_wp
- Definition：A management command (`python manage.py import_wp`) planned for Phase 4 that pulls content from the WordPress REST API (`/wp-json/wp/v2/posts/<id>`, `/wp-json/wp/v2/media`) using an allow-list of post IDs (currently 2734, 2719, 3361). All other posts — including French sports-betting spam injected into the compromised WP site — are excluded and must return HTTP 410 Gone.
- Aliases：WP importer、WordPress importer

### SiteSettings
- Definition：A singleton model (in `apps/core`) intended to hold site-wide configuration such as contact phone numbers, emails, address, hours, and social links — the single source of truth replacing scattered footer/topbar values.
- Aliases：site settings

### legacy redirect middleware
- Definition：Middleware that maps old WordPress query-string URLs (e.g. `/?page_id=9`, `/?p=<id>`, `/?p=<spam-id>`) to new clean slugs (301) or returns 410 Gone for known spam/post paths. Implements the mapping table in CLAUDE.md §2.4.
- Aliases：old URL redirects、WP permalink redirects

### partial responses
- Definition：HTMX fragment responses that render only the `{% partialdef main %}` body (with `<title>`) instead of the full page, used when `request.htmx` is true and not a history restore. They carry `Vary: HX-Request` so CDNs cache them correctly.
- Aliases：HTMX fragments、fragment responses

### unit sidebar swap
- Definition：HTMX pattern on business-unit pages where clicking a unit link in the left sidebar triggers `hx-get` against the same URL and swaps only the main content column (`#unit-content`), keeping the sidebar mounted. Combined with `hx-push-url="true"` so the browser history reflects the selected unit.
- Aliases：unit content swap

### Load More
- Definition：HTMX infinite-scroll pattern on the News list and Gallery: a button with `hx-get="?page=N" hx-target="this" hx-swap="outerHTML"` that fetches the next page of cards and replaces itself; when there are no more results it renders an 'End of Content.' message.
- Aliases：load more button、infinite scroll

### floating call button
- Definition：A fixed-position `tel:` link (+250 786 420 337) visible on all pages, matching the current site's floating telephone button in the footer area.
- Aliases：call button、floating tel button

### RSE listing
- Definition：Reference to Energicotel being listed on the Rwanda Stock Exchange. Appears on the home hero slide ('Investing in a Brighter Future' → bond news post) and in the About page stats ('Years Listed on RSE'). Planned future work includes a dedicated `/investors/` section for annual reports and financial statements.
- Aliases：RSE、Rwanda Stock Exchange listing
