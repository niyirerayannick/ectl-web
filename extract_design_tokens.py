#!/usr/bin/env python3
"""
extract_design_tokens.py — capture the exact design system of energicotel.com
before the WordPress -> Django migration.

Run this ONCE on your own machine (not inside Claude Code's sandbox if it has no
internet), then commit the output folder so Claude Code can read it.

    pip install playwright
    playwright install chromium
    python extract_design_tokens.py

Output (./design_reference/):
    tokens.json              exact values: Elementor global colors/fonts, per-element
                             computed styles, colour/font/size frequency tables
    tokens_summary.md        human-readable summary of the above
    screenshots/<page>_<viewport>.png   full-page screenshots (desktop/tablet/mobile)
    html/<page>.html         rendered HTML of each page (structure reference)
"""
import asyncio
import json
from collections import Counter
from pathlib import Path

from playwright.async_api import async_playwright

BASE = "https://www.energicotel.com"

PAGES = {
    "home": "/",
    "about": "/?page_id=9",
    "board": "/?page_id=1035",
    "management": "/?page_id=2242",
    "unit_power": "/?page_id=2501",
    "unit_gas": "/?page_id=2499",
    "unit_engineering": "/?page_id=2505",
    "unit_solar": "/?page_id=2503",
    "news_list": "/?page_id=11",
    "news_detail_bond": "/?p=2734",
    "gallery": "/?page_id=1040",
    "contact": "/?page_id=12",
}

VIEWPORTS = {"desktop": (1440, 900), "tablet": (768, 1024), "mobile": (390, 844)}

OUT = Path("design_reference")

# Hide the Elementor / Royal Addons newsletter popup so screenshots are clean.
HIDE_POPUPS_CSS = """
.elementor-popup-modal, .dialog-widget, .wpr-template-popup,
.wpr-popup-container, [class*="popup"][role="dialog"] { display:none !important; }
html, body { overflow: auto !important; }
"""

# Elements whose computed style defines the design system.
SELECTORS = {
    "body": "body",
    "h1": "h1", "h2": "h2", "h3": "h3", "h4": "h4", "h5": "h5", "h6": "h6",
    "paragraph": "p",
    "link": "main a, .elementor-widget-text-editor a, a",
    "button_primary": ".elementor-button, .wpr-button, button, input[type=submit]",
    "nav_link": ".elementor-nav-menu a, .wpr-nav-menu a, nav a",
    "nav_dropdown": ".sub-menu a, .elementor-nav-menu--dropdown a, .wpr-sub-menu a",
    "topbar": ".elementor-location-header .elementor-section:first-child, .elementor-location-header .e-con:first-child",
    "header": ".elementor-location-header, header",
    "footer": ".elementor-location-footer, footer",
    "footer_heading": ".elementor-location-footer h2, footer h2",
    "footer_text": ".elementor-location-footer li, .elementor-location-footer p, footer p",
    "input": "input[type=text], input[type=email], textarea",
    "card_image": ".elementor-widget-image img, img",
    "list_item": "main li, .elementor-widget-text-editor li",
}

JS_EXTRACT = r"""
(selectors) => {
  const toHex = (c) => {
    if (!c) return c;
    const m = c.match(/rgba?\(([^)]+)\)/);
    if (!m) return c;
    const p = m[1].split(',').map(s => s.trim());
    const [r, g, b] = p.slice(0, 3).map(Number);
    const a = p[3] !== undefined ? Number(p[3]) : 1;
    if (a === 0) return 'transparent';
    const hex = '#' + [r, g, b].map(v => v.toString(16).padStart(2, '0')).join('');
    return a < 1 ? `${hex} (alpha ${a})` : hex;
  };
  const visible = (el) => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none';
  };
  const pick = (el) => {
    const s = getComputedStyle(el);
    return {
      tag: el.tagName.toLowerCase(),
      classes: (el.className && el.className.baseVal === undefined) ? String(el.className).slice(0, 120) : '',
      text_sample: (el.innerText || '').trim().slice(0, 60),
      color: toHex(s.color),
      background_color: toHex(s.backgroundColor),
      background_image: s.backgroundImage !== 'none' ? s.backgroundImage.slice(0, 200) : null,
      font_family: s.fontFamily,
      font_size: s.fontSize,
      font_weight: s.fontWeight,
      line_height: s.lineHeight,
      letter_spacing: s.letterSpacing,
      text_transform: s.textTransform,
      border_radius: s.borderRadius,
      border: s.borderTopWidth !== '0px' ? `${s.borderTopWidth} ${s.borderTopStyle} ${toHex(s.borderTopColor)}` : null,
      padding: s.padding,
      box_shadow: s.boxShadow !== 'none' ? s.boxShadow : null,
      transition: s.transition !== 'all 0s ease 0s' ? s.transition : null,
      width: Math.round(el.getBoundingClientRect().width),
      height: Math.round(el.getBoundingClientRect().height),
    };
  };

  // 1. Elementor global kit variables (--e-global-color-*, --e-global-typography-*)
  const varNames = new Set();
  for (const sheet of document.styleSheets) {
    let rules; try { rules = sheet.cssRules; } catch (e) { continue; }
    const walk = (list) => {
      for (const r of list) {
        if (r.cssRules) walk(r.cssRules);
        if (!r.style) continue;
        for (const p of r.style) if (p.startsWith('--')) varNames.add(p);
      }
    };
    walk(rules);
  }
  const bodyStyle = getComputedStyle(document.body);
  const rootStyle = getComputedStyle(document.documentElement);
  const cssVars = {};
  for (const n of varNames) {
    const v = (bodyStyle.getPropertyValue(n) || rootStyle.getPropertyValue(n)).trim();
    if (v && (n.includes('global') || n.includes('color') || n.includes('font') ||
              n.includes('typography') || n.includes('container') || n.includes('wpr'))) {
      cssVars[n] = v;
    }
  }

  // 2. Representative element styles
  const elements = {};
  for (const [label, sel] of Object.entries(selectors)) {
    let found = null;
    try { found = [...document.querySelectorAll(sel)].find(visible); } catch (e) {}
    elements[label] = found ? pick(found) : null;
  }

  // 3. Frequency tables across every visible element
  const colors = {}, bgs = {}, fonts = {}, sizes = {}, weights = {}, radii = {};
  const inc = (o, k) => { if (k) o[k] = (o[k] || 0) + 1; };
  for (const el of document.querySelectorAll('body *')) {
    if (!visible(el)) continue;
    const s = getComputedStyle(el);
    const hasText = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (hasText) {
      inc(colors, toHex(s.color));
      inc(fonts, s.fontFamily);
      inc(sizes, s.fontSize);
      inc(weights, s.fontWeight);
    }
    const bg = toHex(s.backgroundColor);
    if (bg && bg !== 'transparent') inc(bgs, bg);
    if (s.borderRadius !== '0px') inc(radii, s.borderRadius);
  }

  // 4. Fonts, icons, emails, meta
  const fontLinks = [...document.querySelectorAll('link[href*="fonts.googleapis"], link[href*="fonts.gstatic"]')].map(l => l.href);
  const iconFonts = [...document.querySelectorAll('link[href*="icon"], link[href*="Material"]')].map(l => l.href);
  const emails = [...new Set([...document.querySelectorAll('a[href^="mailto:"]')].map(a => a.href.replace('mailto:', '')))];
  const phones = [...new Set([...document.querySelectorAll('a[href^="tel:"]')].map(a => a.href.replace('tel:', '')))];
  const meta = {
    title: document.title,
    description: document.querySelector('meta[name=description]')?.content || null,
    og_image: document.querySelector('meta[property="og:image"]')?.content || null,
    favicon: document.querySelector('link[rel*=icon]')?.href || null,
    images_without_alt: [...document.querySelectorAll('img')].filter(i => !i.alt).length,
    total_images: document.querySelectorAll('img').length,
    dom_nodes: document.querySelectorAll('*').length,
  };

  return { cssVars, elements, colors, bgs, fonts, sizes, weights, radii, fontLinks, iconFonts, emails, phones, meta };
}
"""


async def auto_scroll(page):
    """Scroll to the bottom so lazy images, counters and entrance animations fire."""
    await page.evaluate(
        """async () => {
            await new Promise(res => {
                let y = 0; const step = 400;
                const t = setInterval(() => {
                    window.scrollBy(0, step); y += step;
                    if (y >= document.body.scrollHeight) { clearInterval(t); res(); }
                }, 120);
            });
            window.scrollTo(0, 0);
        }"""
    )
    await page.wait_for_timeout(1500)


def top(counter_dict, n=15):
    return Counter(counter_dict).most_common(n)


async def main():
    (OUT / "screenshots").mkdir(parents=True, exist_ok=True)
    (OUT / "html").mkdir(parents=True, exist_ok=True)

    result = {"pages": {}, "breakpoints": {}}
    agg = {k: Counter() for k in ("colors", "bgs", "fonts", "sizes", "weights", "radii")}
    all_emails, all_phones, all_vars = set(), set(), {}

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for vp_name, (w, h) in VIEWPORTS.items():
            ctx = await browser.new_context(viewport={"width": w, "height": h})
            page = await ctx.new_page()
            for name, path in PAGES.items():
                url = BASE + path
                print(f"[{vp_name}] {name}: {url}")
                try:
                    await page.goto(url, wait_until="networkidle", timeout=60000)
                except Exception as e:
                    print(f"   ! load warning: {e}")
                await page.add_style_tag(content=HIDE_POPUPS_CSS)
                await page.keyboard.press("Escape")
                await auto_scroll(page)
                await page.screenshot(path=str(OUT / "screenshots" / f"{name}_{vp_name}.png"), full_page=True)

                data = await page.evaluate(JS_EXTRACT, SELECTORS)
                if vp_name == "desktop":
                    (OUT / "html" / f"{name}.html").write_text(await page.content(), encoding="utf-8")
                    result["pages"][name] = {
                        "url": url,
                        "meta": data["meta"],
                        "elements": data["elements"],
                        "top_text_colors": top(data["colors"]),
                        "top_backgrounds": top(data["bgs"]),
                        "top_font_sizes": top(data["sizes"]),
                    }
                    for k in agg:
                        agg[k].update(data[k])
                    all_vars.update(data["cssVars"])
                    all_emails.update(data["emails"])
                    all_phones.update(data["phones"])
                    result.setdefault("font_links", sorted(set(data["fontLinks"])))
                    result.setdefault("icon_font_links", sorted(set(data["iconFonts"])))
                else:
                    # Record how typography/spacing changes at each breakpoint
                    result["breakpoints"].setdefault(name, {})[vp_name] = {
                        k: (v and {kk: v[kk] for kk in ("font_size", "line_height", "padding", "width")})
                        for k, v in data["elements"].items()
                    }
            await ctx.close()
        await browser.close()

    result["elementor_global_vars"] = dict(sorted(all_vars.items()))
    result["site_wide"] = {k: agg[k].most_common(25) for k in agg}
    result["contact"] = {"emails": sorted(all_emails), "phones": sorted(all_phones)}

    (OUT / "tokens.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    # Human-readable summary
    lines = ["# energicotel.com — extracted design tokens\n"]
    lines.append("## Elementor global variables\n")
    for k, v in result["elementor_global_vars"].items():
        if "global" in k:
            lines.append(f"- `{k}`: `{v}`")
    for title, key in [("Text colours", "colors"), ("Background colours", "bgs"),
                       ("Font families", "fonts"), ("Font sizes", "sizes"),
                       ("Font weights", "weights"), ("Border radii", "radii")]:
        lines.append(f"\n## {title} (site-wide frequency)\n")
        for val, n in result["site_wide"][key]:
            lines.append(f"- `{val}` — {n}")
    lines.append("\n## Key elements (home page, desktop)\n")
    for label, el in result["pages"]["home"]["elements"].items():
        if el:
            lines.append(f"- **{label}**: {el['font_family'].split(',')[0]} {el['font_size']}/"
                         f"{el['line_height']} w{el['font_weight']}, color {el['color']}, "
                         f"bg {el['background_color']}, radius {el['border_radius']}")
    lines.append("\n## Contact data found\n")
    lines.append(f"- Emails: {', '.join(result['contact']['emails']) or 'none found'}")
    lines.append(f"- Phones: {', '.join(result['contact']['phones']) or 'none found'}")
    lines.append(f"\n## Font stylesheets\n")
    lines += [f"- {u}" for u in result.get("font_links", [])]
    (OUT / "tokens_summary.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"\nDone. See {OUT}/tokens_summary.md and {OUT}/screenshots/")


if __name__ == "__main__":
    asyncio.run(main())
