---
kind: frontend_style
name: Tailwind CSS v4 Design Tokens + Elementor Parity Migration
category: frontend_style
scope:
    - '**'
source_files:
    - theme/static_src/src/styles.css
    - design_reference/tokens.json
    - design_reference/tokens_summary.md
    - CLAUDE.md
    - templates/base.html
    - extract_design_tokens.py
---

## Approach

The site is being rebuilt from a WordPress/Elementor installation into Django 5.2 with **Tailwind CSS v4** via `django-tailwind-cli` (no Node toolchain). The styling system is intentionally token-driven: every visual value (colours, fonts, type scale, radii, breakpoints) is extracted from the live site by `extract_design_tokens.py` and committed as `design_reference/tokens.json` plus `design_reference/tokens_summary.md`. The single source of truth for Tailwind configuration is the `@theme` block in `theme/static_src/src/styles.css`; templates consume it through generated utility classes (`bg-brand-primary`, `text-heading`, …) rather than arbitrary values.

## Key files

- `theme/static_src/src/styles.css` — Tailwind entry point; `@import "tailwindcss"`, `@source` declarations pointing at `templates/` while explicitly excluding `design_reference/` and `static/js/vendor/`, and an empty `@theme { ... }` scaffold awaiting Phase 2 population.
- `design_reference/tokens.json` (5944 lines) — per-page DOM analysis output containing element-level styles (color, background_color, font_family, font_size, font_weight, line_height, letter_spacing, border_radius, box_shadow, transition), plus frequency histograms (`top_text_colors`, `top_backgrounds`, `top_font_sizes`) used to derive design tokens.
- `design_reference/tokens_summary.md` — human-readable summary of Elementor global variables (`--e-global-color-*`, `--e-global-typography-*`), top colour/font/radius frequencies, and key-element specs (body, h1–h6, paragraph, link, nav_link, button_primary).
- `CLAUDE.md` §5 — prescriptive mapping of Elementor globals → Tailwind `@theme` tokens (`brand-primary`, `brand-secondary`, `accent`, `heading`, `body`, `topbar-bg`, `footer-bg`, `font-heading`, `font-body`, responsive type scale, radii, container width, breakpoints `md=768px` / `lg=1025px`).
- `templates/base.html` — includes `{% tailwind_css %}` (built by `python manage.py tailwind build`) and vendors HTMX 2 + Alpine.js 3 under `static/js/vendor/`.
- `extract_design_tokens.py` — owner-run script that captures the live site's computed styles into `design_reference/`.

## Architecture & conventions

1. **CSS-first Tailwind v4 config.** All design values are declared inside `@theme` in `styles.css`; no `tailwind.config.js` is used because the project uses the CSS-first Tailwind v4 API via `django-tailwind-cli`.
2. **Token utilities only.** Templates must use generated utilities derived from the `@theme` block (e.g. `bg-brand-primary`, `text-heading`) and must not write raw hex values or ad-hoc sizes in markup.
3. **Elementor parity rule.** Visual reproduction takes priority over improvement: colours, fonts, sizes, spacing, layout must match the live site exactly using values from `tokens.json`/`tokens_summary.md`. No Elementor class names may be copied into new code.
4. **Responsive strategy mirrors Elementor defaults.** Breakpoints are set to `--breakpoint-md: 768px` and `--breakpoint-lg: 1025px` to match Elementor's mobile ≤767 / tablet ≤1024 convention. Screenshots under `design_reference/screenshots/<page>_{desktop,tablet,mobile}.png` are the acceptance criteria at 1440 / 768 / 390 px.
5. **Fonts.** The live site uses Inter, Kanit, Roboto, Helvetica, Lato, Poppins, Nunito Sans (per `tokens_summary.md`); the migration plan calls for self-hosting them (Google Fonts link or `@fontsource`) rather than relying on external CDNs.
6. **Icons.** Material Icons ligatures (`visibility`, `track_changes`, `handshake`) are used on the live site; the spec recommends a self-hosted subset or inline SVG equivalents.
7. **Interactivity layer.** HTMX 2 provides SPA navigation (`hx-boost` on `<main id="main">`), Alpine.js 3 handles small UI state (dropdowns, drawer, lightbox, tabs). Both are loaded deferred from `static/js/vendor/`.
8. **Build pipeline.** `python manage.py tailwind build` compiles `theme/static_src/src/styles.css` → `theme/static_src/dist/css/styles.css`, served via WhiteNoise as `/static/css/styles.css`.

## Conventions & constraints

- **Design values live in one place** (`theme/static_src/src/styles.css` `@theme` block). Templates use token utilities (`bg-brand-primary`, `text-heading`), never arbitrary values like `text-[#1a2b3c]` — enforced by the CLAUDE.md ground rules (§0.1, §5).
- **Never copy WordPress/Elementor markup or CSS.** Rebuild each section with semantic HTML + Tailwind utilities; no Elementor class names in the new code — enforced by CLAUDE.md §0.2.
- **Every page must work without JavaScript** (plain links + full page loads). HTMX is progressive enhancement — enforced by CLAUDE.md §0.4.
- **Visual parity first, improvements second.** Phase 1–5 must reproduce the current look using values in `design_reference/tokens.json`; never invent a hex code or font size — enforced by CLAUDE.md §0.1.
- **Breakpoints match Elementor defaults:** `--breakpoint-md: 768px`, `--breakpoint-lg: 1025px` — stated in both `styles.css` and CLAUDE.md §5.
- **Screenshots under `design_reference/screenshots/` are the acceptance criteria** for parity at 1440 / 768 / 390 px widths — stated in CLAUDE.md §0.6 and §4.
- **Accessibility:** colour contrast ≥ 4.5:1 for body text; keep original failing colours only for decoration and add a darker token for text — stated in CLAUDE.md §5.
- **Respect `prefers-reduced-motion`** for sliders, counters, entrance animations — stated in CLAUDE.md §5.