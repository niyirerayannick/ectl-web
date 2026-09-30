# ENERGICOTEL (ECTL) PLC — WordPress → Django + Tailwind + HTMX migration spec

> Put this file at the root of the new repository as `CLAUDE.md`.
> Claude Code reads it automatically at the start of every session.
> Source site: https://www.energicotel.com (WordPress + Elementor 3.34.2 + Royal Elementor Addons)

---

## 0. Ground rules for Claude Code

1. **Visual parity first, improvements second.** Phase 1–5 must reproduce the current look (colours, fonts, sizes, spacing, layout) using the values in `design_reference/tokens.json` and the screenshots in `design_reference/screenshots/`. Never invent a hex code or font size; if a value is missing from `tokens.json`, stop and ask.
2. **Never copy WordPress/Elementor markup or CSS.** Rebuild each section with semantic HTML + Tailwind utilities. No Elementor class names in the new code.
3. **All design values live in one place** (`theme/static_src/src/styles.css` `@theme` block). Templates use token utilities (`bg-brand-primary`, `text-heading`), never arbitrary values like `text-[#1a2b3c]`.
4. **Every page must work without JavaScript** (plain links + full page loads). HTMX is progressive enhancement.
5. **Do not import any of the spam posts listed in §2.1.** Import only allow-listed content.
6. Work phase by phase (§9). At the end of each phase: run tests, run `python manage.py check --deploy` (from Phase 7), and compare against the screenshots at 1440 / 768 / 390 px widths.

---

## 1. Tech stack

| Layer | Choice | Notes |
|---|---|---|
| Backend | Django 5.2 LTS, Python 3.12+ | Django 6.0 is fine too (it has built-in template partials) |
| DB | PostgreSQL (SQLite in dev) | |
| Templates | Django templates + `django-template-partials` | `{% partialdef %}` for HTMX fragments |
| CSS | Tailwind CSS v4 via `django-tailwind-cli` | No Node needed; CSS-first `@theme` config |
| Interactivity | HTMX 2.x + `django-htmx` | `hx-boost` for SPA navigation |
| Small UI state | Alpine.js 3 | Dropdowns, mobile drawer, lightbox, tabs |
| Carousels | Swiper 11 (or a small Alpine carousel) | Hero slider + unit-page image sliders |
| Images | `django-imagekit` or `sorl-thumbnail`, WebP + `srcset` | |
| Rich text | `django-prose-editor` or TinyMCE in admin; sanitise with `nh3` | |
| Admin | Django admin + `django-unfold` theme | Editors manage all content |
| Static | WhiteNoise | |
| Server | Gunicorn behind Nginx; Cloudflare stays in front | |
| Forms | Django forms + honeypot + `django-ratelimit` | Contact form emails via SMTP |
| SEO | `django.contrib.sitemaps`, per-page meta, JSON-LD Organization | |

---

## 2. Findings from the analysis of the live site (read before building)

### 2.1 CRITICAL — the WordPress site is compromised with SEO spam
The Blog ("News and Events") is filled with French-language sports-betting articles unrelated to ECTL, all dated **August 26, 2026**, e.g. post IDs **3368–3387** (tennis de table, paris rugby, biathlon, UFC, boxe, NHL, crypto betting…). They occupy at least the first two pages of the blog, and the "Most Recent Posts" sidebar on real articles also shows them.

- This is a typical injected-spam compromise. It is urgent independently of the migration (reputation of an RSE-listed company, Google penalties).
- Immediate actions for the site owner (outside Claude Code): change all WP-admin, hosting, FTP and DB passwords; remove unknown admin users; update WordPress core, Elementor and Royal Elementor Addons (the latter has had serious security vulnerabilities in the past); delete spam posts; scan for backdoors (`wp-content/uploads/*.php`, modified theme files); request removal of spam URLs in Google Search Console.
- **Migration rule:** the importer (Phase 4) uses an **allow-list** of post IDs. Known legitimate posts: `2734` (bond listing), `2719`, `3361` (linked from 2734 — verify content). Everything else is excluded unless the owner confirms it.
- All spam URLs (`/?p=3368` … `/?p=3387` and any others found) must return **HTTP 410 Gone** on the new site.

### 2.2 Theme leftovers to remove (not ECTL content)
- Site-wide popup "Subscribe And Enjoy! / VIP Services / 1 Month VIP by signing up to our newsletter" — demo content from the theme. **Do not rebuild.** (Optional: a simple real newsletter field in the footer — ask owner.)
- Blog categories "Exterior Design", "Interior Design", "Landscaping", "Management" — theme demo categories. Replace with ECTL categories (e.g. Corporate News, Investor Relations, Projects, Events).
- Gallery "like" counters (Royal Addons `wpr_likes`) — drop.
- The header/nav markup is duplicated ~6 times in the DOM (desktop, sticky, mobile variants). New site: **one** header, responsive.

### 2.3 Content errors to fix during migration (confirm with owner)
| Page | Issue | Suggested fix |
|---|---|---|
| ECTL Power | "RWF 2.06 Billion (approx. EUR 2.06 million)" — conversion is wrong (RWF 2.06 bn is not EUR 2.06 m) | Owner to confirm correct EUR/USD figure |
| About | Stats counters show "0 +" (animated counters that start at 0) | Store real values in DB (e.g. installed MW 3.2, years of experience, years listed on RSE) and render the final number server-side; animate only as enhancement |
| Senior Management | "Cordinator", "Adminstration" typos | Coordinator, Administration |
| ECTL Gas | "Scheduled to launch in early 2026" / home "Launching in 2026" — today is past that | Update to current status |
| ECTL Solar | Hero slide hot-links an Unsplash image | Replace with own/licensed image stored locally |
| Home hero | "Powering Africa's Future, Sustainability" reads awkwardly | e.g. "Powering Africa's Future Sustainably" |
| Footer | Social links point to **EPC Africa Group** accounts, labelled "Twitter" | Confirm whether ECTL has its own accounts; relabel as X |
| Address | Three variants: "KG436St Gacuriro Kigali", "Gacuriro KG 436 St", "Gasabo - Gacuriro KG 436St Plot No:6A" | One canonical address in `SiteSettings` |
| Images | Many images have empty `alt`; filenames like `WhatsApp-Image-2025-…jpg` | Rename on import, write alt text |
| Power page | Page heading "ECTL Power (Hydro)" vs menu "ECTL Power" | Keep consistent |

### 2.4 URLs
WordPress permalinks are disabled (`?page_id=`, `?p=`). New site uses clean slugs + permanent redirects. Django URL routing ignores query strings, so redirects are done by a **middleware** that reads `request.GET`:

| Old URL | New URL | Status |
|---|---|---|
| `/` | `/` | — |
| `/?page_id=9` | `/about/` | 301 |
| `/?page_id=1035` | `/about/board/` | 301 |
| `/?page_id=2242` | `/about/management/` | 301 |
| `/?page_id=2501` | `/business-units/power/` | 301 |
| `/?page_id=2499` | `/business-units/gas/` | 301 |
| `/?page_id=2505` | `/business-units/engineering/` | 301 |
| `/?page_id=2503` | `/business-units/solar/` | 301 |
| `/?page_id=11` (+ `&paged=N`) | `/news/` (+ `?page=N`) | 301 |
| `/?page_id=1040` | `/gallery/` | 301 |
| `/?page_id=12` | `/contact/` | 301 |
| `/?p=2734` | `/news/ectl-lists-oversubscribed-corporate-bond-rse/` | 301 |
| `/?p=<allow-listed id>` | `/news/<slug>/` (store `wp_id` on Post) | 301 |
| `/?p=<spam id>` | — | 410 |
| `/wp-admin*`, `/wp-login.php`, `/xmlrpc.php`, `/wp-content/*.php` | — | 410 |
| `/wp-content/uploads/...` images | new media URL (keep a map) | 301 |

### 2.5 Things I could NOT read remotely (why the extraction script exists)
- Exact colours, fonts, font sizes, spacing, radii, shadows (Elementor loads them from external CSS).
- Email addresses (hidden by Cloudflare email obfuscation).
- Animations/entrance effects and slider timings.

`extract_design_tokens.py` (run by the owner, see §9 Phase 0) captures all of these into `design_reference/`.

---

## 3. Sitemap & navigation (keep identical)

```
Top bar:  phone 1 / phone 2 | email 1 / email 2 | KG436St Gacuriro Kigali · Mon–Fri 9:00AM–5:00PM
Header:   Logo (Logo-Tr-01.png; Logo-Retina.png for 2x)
Nav:
  Home
  Who we are ▾   About · Board Members · Senior Management
  What we do ▾   ECTL Power · ECTL Gas · ECTL Engineering · ECTL Solar
  Media Center ▾ Blog · Gallery
  Contact
Footer:   white logo · Social Media Channels (X, Instagram, LinkedIn, YouTube)
          Quick Links (Power, Gas, Solar, Engineering)
          Contact Info (phone, email, address) · © {current year} Energicotel Plc
          Floating tel: button (+250) 786 420 337
```

Contact data (source of truth goes into `SiteSettings`):
- Phones: (+250) 786 420 337, (+250) 788 207 637
- Emails: take from `design_reference/tokens.json` → `contact.emails`
- Address: Gasabo – Gacuriro, KG 436 St, Plot No. 6A, Kigali (confirm)
- Hours: Mon–Fri 9:00 AM – 5:00 PM

---

## 4. Page-by-page analysis → components

Reference screenshots: `design_reference/screenshots/<page>_{desktop,tablet,mobile}.png`.

### 4.1 Home `/`
1. **Hero slider** (3 slides, each: H2 title, subtitle, "Discover More" button, background image)
   - "Powering Africa's Future, Sustainability" → Engineering
   - "Your Trusted Energy Producer" → Power
   - "Investing in a Brighter Future" (RSE listing) → bond news post
2. **Who We Are / About Us** — eyebrow "Energicotel PLC - Your Energy Provider", intro paragraph, two buttons (About Us, About EPC Africa → epcafrica.com, external), **7-image collage/slider**.
3. **Vision / Mission / Values** — 3 icon cards (Material icons: `visibility`, `track_changes`, `handshake`).
4. **Our Business Units** — 4 cards: name, category label, description, 4 bullet highlights each.
5. **Our Partners** — 6 logo images (strip/marquee).
6. Footer.
Models: `HeroSlide`, `CoreValue`, `BusinessUnit` (+`UnitHighlight`), `Partner`, `SiteSettings`.

### 4.2 About `/about/`
Page-title banner "About" → same intro + image collage as home → Vision/Mission/Values → **Overview "What We've Achieved"** stats: Mega Watts, Years of Experience, Years Listed on RSE (animated counters) → **CTA banner** "Work With Us! / Have Any Upcoming Project? / Looking for Quality and Affordable Services…" + Contact us button.
Models: `Stat`, reuse `CoreValue`. Reusable components: `page_banner`, `cta_banner`, `stat_counter`.

### 4.3 Board Members `/about/board/`
Grid of person cards (photo, name, role): Felicien MUVUNYI – Chairman; Ferdy TURASENGA – Executive Director; Lena Militisi Muhongerwa, Prof Josiah Lange Munda, Silvie Kayitesi Kanimba, Justin MUDAKIKWA – Board Members.
### 4.4 Senior Management `/about/management/`
Same card component: Pascaline UMUTESI – Company Secretary; Blaise MUNYEMANA – Director of Research and Consultancy; Honore MUGIRANEZA – Coordinator of Operations and Management; Sam KAGORORA – Director of Administration and Finance.
Model: `Person(group=board|management, order)`. Optional enhancement: click card → HTMX modal with bio.

### 4.5 Business unit pages `/business-units/<slug>/` (one template for all 4)
Shared layout:
- Page banner: unit name + tagline (Power: "Sustainable Hydropower Generation for Rwanda"; Gas: "Powering Growth with Clean Energy Solutions"; Engineering: "World-Class Engineering Consultancy"; Solar: "Innovating for a Brighter Future").
- **Sidebar**: "What we do" (links to the 4 units, current one highlighted) + "Contact us" box (address, hours, 2 phones, 2 emails).
- **Image slider** with ‹ › arrows.
- Ordered **content sections** (H2 + rich text / bullet list).
- **CTA strip** (H3 sentence + Contact us button).

Unit-specific content:
- **Power**: Introduction (IPP, 3 HPPs, Western Province, 3.2 MW total); Operational Assets list (Keya 2.2 MW, Nkora 0.68 MW, Cyimbili 0.3 MW); Engineering & Rehabilitation Expertise; Scope of Works; Investment. Home card also lists Lihanda HPP (Kenya) – under development.
- **Gas**: Strategic Expansion (2026); Services & Solutions list (Wholesale & Distribution, Refilling & Storage, Flexible Distribution Models).
- **Engineering**: Overview; Featured Project Portfolio — 5 projects each with Role / Scope / Value: Rusizi Port Construction (USD 12.4 M), Regional Rusumo Falls HEP 80 MW (sub-consultant to AECOM), Nyabarongo Substation & Feeder Upgrade (USD 4.29 M), Kilinda Substation Upgrade (USD 970,665), Akagera Game Lodge Upgrade (RWF 1.08 bn).
- **Solar**: Our Solar Mission; Core Competencies list.
Models: `BusinessUnit`, `UnitImage`, `UnitSection` (heading, body, order), `Project` (unit FK, title, role, scope, value_amount, currency, order), `PowerAsset` (name, capacity_mw, location, status).
HTMX: sidebar unit links swap only the main column (`hx-target="#unit-content"`, `hx-push-url="true"`) — feels instant.

### 4.6 News list `/news/` ("News and Events")
Card list: title, date, excerpt, Read More; "Load More" button ("End of Content." when finished).
HTMX: Load More = `hx-get="?page=N" hx-target="this" hx-swap="outerHTML"` returning next cards + new button. Category filter chips swap the list.
### 4.7 News detail `/news/<slug>/`
H1, featured image, rich body (bold phrases), image gallery grid (lightbox), prev/next post links, sidebar "Most Recent Posts" + categories. **Drop WP comments** (spam vector); if wanted later, use a moderated form.
Model: `Post(wp_id, title, slug, excerpt, body, cover, published_at, status, category)`, `PostImage`.

### 4.8 Gallery `/gallery/`
Masonry/grid of photos, "Load More". HTMX infinite scroll (`hx-trigger="revealed"`) + Alpine lightbox with keyboard/swipe. No likes. Optional albums (Power sites, Events, Bond listing…).
Model: `GalleryImage(image, caption, alt, album, order, taken_at)`.

### 4.9 Contact `/contact/`
Three info blocks (Email, Telephone, Location) + form (Your name*, Email address*, Subject*, Your message optional) + recommended: embedded map (OpenStreetMap iframe or static image; Google Maps needs a key).
HTMX: `hx-post` → returns form partial with inline errors or a success message; honeypot + rate-limit; email to company inbox + save `ContactMessage` in DB.

### 4.10 Global
- 404 / 500 pages in site style.
- Floating call button (tel link) as on current site.
- Scroll-to-top button.

---

## 5. Design system (fill from `design_reference/tokens.json`)

Claude Code: open `design_reference/tokens_summary.md` and `tokens.json`, then fill this block in `theme/static_src/src/styles.css`. Map Elementor globals as follows:
`--e-global-color-primary` → `brand-primary`, `--e-global-color-secondary` → `brand-secondary`, `--e-global-color-text` → `body`, `--e-global-color-accent` → `accent`; any extra `--e-global-color-<id>` → named by where it is used (check screenshots). Typography: `--e-global-typography-primary-font-family` → `--font-heading`, `…-text-font-family` → `--font-body`.

```css
@import "tailwindcss";

@theme {
  /* COLOURS — exact hex from tokens.json, do not approximate */
  --color-brand-primary:   /* e-global-color-primary */;
  --color-brand-secondary: /* e-global-color-secondary */;
  --color-accent:          /* e-global-color-accent  (buttons/links) */;
  --color-heading:         /* h2 color */;
  --color-body:            /* paragraph color */;
  --color-topbar-bg:       /* elements.topbar.background_color */;
  --color-footer-bg:       /* elements.footer.background_color */;
  --color-footer-text:     /* elements.footer_text.color */;
  --color-surface:         /* most frequent light section bg */;
  --color-border:          /* input border */;

  /* FONTS — same families as the live site (self-host via @fontsource or Google Fonts link) */
  --font-heading: /* h2 font_family */;
  --font-body:    /* body font_family */;

  /* TYPE SCALE — desktop values from elements.*; responsive values from breakpoints.* */
  --text-h1: ; --text-h1--line-height: ;
  --text-h2: ; --text-h2--line-height: ;
  --text-h3: ; --text-h4: ; --text-h5: ; --text-h6: ;
  --text-body: ; --text-body--line-height: ;
  --text-nav: ;  --text-small: ;

  /* SHAPE */
  --radius-btn:  /* button_primary.border_radius */;
  --radius-card: /* most frequent radius */;
  --shadow-card: /* box_shadow of cards */;

  /* LAYOUT — Elementor container width (e.g. --container-max-width) */
  --container-site: ;

  /* BREAKPOINTS — Elementor defaults: mobile ≤767, tablet ≤1024; match them */
  --breakpoint-md: 768px;
  --breakpoint-lg: 1025px;
}
```

Rules:
- Headings get responsive sizes matching `breakpoints.<page>.{tablet,mobile}` in tokens.json.
- Icons: the site uses Google Material Icons ligatures (`visibility`, `track_changes`, `handshake`) → use Material Symbols (self-hosted subset) or inline SVG equivalents.
- Buttons: one `btn` component (`primary`, `outline`, `light`) matching `button_primary` styles incl. hover state (check screenshots / live site hover).
- Respect `prefers-reduced-motion` for sliders, counters and entrance animations.
- Accessibility: colour contrast ≥ 4.5:1 for body text; if an original colour fails, keep it for decoration and add a darker token for text — report it.

---

## 6. Project structure

```
energicotel/
├── CLAUDE.md
├── design_reference/            # output of extract_design_tokens.py (committed)
├── config/                      # settings/{base,dev,prod}.py, urls.py, wsgi.py
├── apps/
│   ├── core/        # SiteSettings (singleton), HeroSlide, CoreValue, Stat, Partner,
│   │                # home/about views, legacy-redirect middleware, sitemaps, context processor
│   ├── team/        # Person
│   ├── units/       # BusinessUnit, UnitImage, UnitSection, UnitHighlight, Project, PowerAsset
│   ├── news/        # Category, Post, PostImage, import_wp management command
│   ├── gallery/     # Album, GalleryImage
│   └── contact/     # ContactMessage, form, email
├── templates/
│   ├── base.html                # full shell: <head>, topbar, header, #main, footer
│   ├── partials/                # header.html, nav.html, footer.html, topbar.html
│   ├── components/              # page_banner, section_heading, btn, value_card, unit_card,
│   │                            # partner_strip, stat_counter, cta_banner, person_card,
│   │                            # post_card, load_more, image_slider, lightbox, unit_sidebar
│   ├── core/ team/ units/ news/ gallery/ contact/
│   └── errors/ 404.html 500.html
├── theme/static_src/src/styles.css
└── static/ (js/app.js, img/, fonts/)
```

---

## 7. HTMX "SPA" behaviour — implementation rules

1. `base.html`:
   ```html
   <body hx-boost="true"
         hx-target="#main" hx-select="#main" hx-swap="outerHTML show:window:top"
         hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'
         hx-indicator="#page-progress">
   ```
   Header/footer stay mounted; only `<main id="main">` changes.
2. **Partial responses**: views render a `{% partialdef main %}` fragment when `request.htmx` is true **and** `not request.htmx.history_restore_request`; otherwise the full page. Include `<title>` inside the fragment so htmx updates the document title.
3. **Caching**: add `Vary: HX-Request` (use `django_htmx` + `patch_vary_headers`) so Cloudflare/browsers never serve a fragment as a full page. Set Cloudflare to bypass cache for HTML, or respect `Vary`.
4. **Active nav state**: on `htmx:afterSettle`, JS toggles `aria-current="page"` on nav links matching `location.pathname` (and parent dropdown). Close mobile drawer and dropdowns on navigation.
5. **Re-initialisation**: sliders/counters/lightbox initialise on `htmx.onLoad(el => …)` (not `DOMContentLoaded`). Alpine auto-initialises swapped content.
6. **Progress bar**: thin top bar `#page-progress` shown during requests (`htmx-request` class).
7. **Opt-outs**: `hx-boost="false"` on `/admin/`, file downloads (PDF reports), and external links (htmx ignores cross-origin anyway).
8. **Focus & a11y**: after swap move focus to the new `<h1>` (`tabindex="-1"`), announce page title in an `aria-live="polite"` region.
9. **Scroll**: `show:window:top` for navigation; history back restores scroll (htmx default).
10. **Errors**: handle `htmx:responseError` → fall back to full navigation (`location.href = url`).
11. **Prefetch** (optional): htmx `preload` extension on nav links (`hx-ext="preload"`, `preload="mouseover"`).
12. **Forms**: contact form posts with `hx-post`, targets its own wrapper, returns 200 with errors (HTMX 2 does not swap 4xx by default — keep 200 or configure `responseHandling`).

Per-feature HTMX patterns: unit sidebar (swap unit column), news Load More (`outerHTML` on button), news category filter (`hx-get` + `hx-push-url`), gallery infinite scroll (`hx-trigger="revealed"`), person bio modal (`hx-get` into `#modal`), contact form (`hx-post`).

---

## 8. Content & media migration

- `python manage.py import_wp --base https://www.energicotel.com --allow 2734,2719,3361` uses the WP REST API (`/wp-json/wp/v2/posts/<id>`, `/wp-json/wp/v2/media`) and **only** imports allow-listed IDs. Store `wp_id`. Sanitise HTML with `nh3` (allow p, strong, em, a, ul, ol, li, h2–h4, img, figure, figcaption, blockquote). Rewrite image URLs to local media.
- Pages content (About, units, people, projects, stats, partners, hero slides) is small: seed it with a **data migration / fixture** (`apps/*/fixtures/initial.json`) typed from §4 — faster and cleaner than parsing Elementor JSON.
- Media: download only images referenced by the kept content (list in `design_reference/html/*.html`), rename to meaningful slugs (`keya-hpp-intake.jpg`), strip EXIF, generate WebP + 3 widths. Record `old_url → new_url` in `apps/core/legacy_media.json` for 301s.
- If WP REST API is disabled/blocked, fall back to an owner-provided WordPress XML export (Tools → Export) and parse it with the same allow-list.

---

## 9. Phases for Claude Code (one prompt per phase)

**Phase 0 — Design reference (owner runs locally, before Claude Code)**
`pip install playwright && playwright install chromium && python extract_design_tokens.py` → commit `design_reference/`.

**Phase 1 — Scaffold**
"Read CLAUDE.md. Create the Django 5.2 project per §1 and §6: settings split, apps, django-htmx, django-template-partials, django-tailwind-cli with Tailwind v4, Alpine, HTMX 2, WhiteNoise, Postgres via DATABASE_URL, django-unfold admin. Add a README with run commands. Add pytest + pytest-django. No pages yet."
Done when: `runserver` works, `tailwind` builds, tests pass.

**Phase 2 — Design tokens + base layout**
"Using design_reference/tokens_summary.md, tokens.json and the screenshots, fill the @theme block (§5) with exact values, then build base.html, topbar, header with 3 dropdowns, mobile drawer, footer, floating call button, 404/500. Compare with home_desktop/tablet/mobile screenshots and list any differences."
Done when: header/footer match screenshots at 1440/768/390 px.

**Phase 3 — Models, admin, seed data**
"Implement the models in §4 with admin (inlines, ordering, image previews) and SiteSettings singleton + context processor. Seed all content from §4 via fixtures, applying the fixes in §2.3 marked 'confirmed' (leave TODO markers for unconfirmed ones)."

**Phase 4 — Pages**
"Build Home, About, Board, Management, the unit detail template, News list/detail, Gallery, Contact using reusable components in templates/components/. Match screenshots. Then write the import_wp command (§8) with allow-list and run it."

**Phase 5 — HTMX SPA layer**
"Implement every rule in §7, including Vary header, partial rendering, active nav, re-init, progress bar, focus management, Load More, infinite gallery, unit sidebar swap, contact hx-post. Add tests asserting fragment vs full responses and the Vary header."

**Phase 6 — SEO, redirects, security**
"Implement the legacy redirect middleware and 410 list (§2.4), sitemap.xml, robots.txt, canonical tags, per-page meta description + Open Graph, JSON-LD Organization, image alt enforcement in admin. Tests for every old URL in §2.4."

**Phase 7 — Performance & deploy**
"Lighthouse ≥ 90 on mobile for all pages: WebP/srcset, lazy loading, font-display swap + preload, minified CSS, defer JS. Production settings (`check --deploy` clean), Gunicorn, Nginx sample config, Dockerfile, backup notes."

---

## 10. Recommended improvements (after parity is approved)

1. **Investor Relations section** — ECTL is listed on the Rwanda Stock Exchange; add `/investors/` with annual reports, financial statements, AGM notices, bond programme documents and press releases (downloadable PDFs, `Document` model with year/type filters via HTMX). This is the single most valuable addition for a PLC.
2. ECTL-own social accounts (currently EPC Africa's).
3. Real, admin-editable stats instead of "0 +".
4. Project map (Keya, Nkora, Cyimbili, Rusizi, Rusumo…) with Leaflet + OpenStreetMap.
5. Multilingual (English / Kinyarwanda / French) using Django i18n — structure templates with `{% translate %}` from the start.
6. Consistent professional photography replacing WhatsApp images.
7. Security headers (CSP allowing only self + needed CDNs), admin on a non-default path, 2FA for admin (`django-otp`).
8. Uptime + error monitoring (Sentry), daily DB and media backups.
