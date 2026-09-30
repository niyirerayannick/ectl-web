#!/usr/bin/env python3
"""
resume_extract.py — crash-safe resume of extract_design_tokens.py.

Reuses the constants and the extraction JS from extract_design_tokens.py
(imported as a module, not modified). Skips artifacts already captured
validly, retries failures, and persists progress to _progress.json after
every page so a crash (e.g. disk full) never loses work.

Delete this file once the extraction is fully verified.
"""
import asyncio
import json
import shutil
import sys
from collections import Counter
from pathlib import Path

import extract_design_tokens as edt
from playwright.async_api import async_playwright

OUT = edt.OUT
STATE_FILE = Path("_progress.json")
MIN_PNG_BYTES = 100 * 1024          # a valid full-page PNG is always > 100 KB
MIN_HTML_BYTES = 10 * 1024          # a valid rendered page is always > 10 KB
MIN_FREE_MB = 150                   # refuse to write below this
ATTEMPTS = 3
PAUSE_BETWEEN_ATTEMPTS = 20         # seconds


def free_mb():
    return shutil.disk_usage(".").free // (1024 * 1024)


def png_looks_valid(p: Path) -> bool:
    try:
        if p.stat().st_size < MIN_PNG_BYTES:
            return False
        with open(p, "rb") as f:
            head = f.read(8)
            if head != b"\x89PNG\r\n\x1a\n":
                return False
            f.seek(-16, 2)
            return b"IEND" in f.read()
    except OSError:
        return False


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {
        "desktop": {}, "breakpoints": {}, "emails": [], "phones": [],
        "vars": {}, "font_links": [], "icon_font_links": [], "failures": [],
    }


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


async def capture_png(page, path: Path, state, tag):
    """Write a full-page screenshot with retries; never raises."""
    if png_looks_valid(path):
        print(f"   screenshot up-to-date, skipping ({tag})")
        return True
    for attempt in range(1, ATTEMPTS + 1):
        while free_mb() < MIN_FREE_MB:
            print(f"   low disk: {free_mb()} MB free, waiting 30 s ({tag})")
            await asyncio.sleep(30)
        try:
            await page.screenshot(path=str(path), full_page=True)
            if png_looks_valid(path):
                return True
            print(f"   ! invalid PNG written, retry {attempt}/{ATTEMPTS} ({tag})")
        except Exception as e:  # noqa: BLE001 — keep going, report at the end
            print(f"   ! screenshot failed ({tag}): {e}")
        if attempt < ATTEMPTS:
            await asyncio.sleep(PAUSE_BETWEEN_ATTEMPTS)
    state["failures"].append(f"screenshot:{tag}")
    save_state(state)
    return False


async def goto_with_retry(page, url, tag):
    for attempt in range(1, ATTEMPTS + 1):
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            return True
        except Exception as e:  # noqa: BLE001
            print(f"   ! load attempt {attempt}/{ATTEMPTS} failed ({tag}): {e}")
            if attempt < ATTEMPTS:
                await asyncio.sleep(PAUSE_BETWEEN_ATTEMPTS)
    return False


def artifacts_complete(state):
    """True when every deliverable already exists on disk and in the state file."""
    for name in edt.PAGES:
        if name not in state["desktop"]:
            return False
        bps = state["breakpoints"].get(name, {})
        if not ("tablet" in bps and "mobile" in bps):
            return False
        if not (OUT / "html" / f"{name}.html").exists():
            return False
        for vp in edt.VIEWPORTS:
            if not png_looks_valid(OUT / "screenshots" / f"{name}_{vp}.png"):
                return False
    return True


async def capture_all(state):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        try:
            for vp_name, (w, h) in edt.VIEWPORTS.items():
                ctx = await browser.new_context(viewport={"width": w, "height": h})
                page = await ctx.new_page()
                for name, path in edt.PAGES.items():
                    url = edt.BASE + path
                    tag = f"{name}_{vp_name}"
                    print(f"[{vp_name}] {name}: {url}  ({free_mb()} MB free)")
                    try:
                        await goto_with_retry(page, url, tag)
                        await page.add_style_tag(content=edt.HIDE_POPUPS_CSS)
                        await page.keyboard.press("Escape")
                        await edt.auto_scroll(page)
                        await capture_png(
                            page, OUT / "screenshots" / f"{tag}.png", state, tag
                        )

                        data = await page.evaluate(edt.JS_EXTRACT, edt.SELECTORS)

                        if vp_name == "desktop":
                            html_path = OUT / "html" / f"{name}.html"
                            if not html_path.exists() or html_path.stat().st_size < MIN_HTML_BYTES:
                                html_path.write_text(await page.content(), encoding="utf-8")
                            record = {
                                "url": url,
                                "meta": data["meta"],
                                "elements": data["elements"],
                                "top_text_colors": edt.top(data["colors"]),
                                "top_backgrounds": edt.top(data["bgs"]),
                                "top_font_sizes": edt.top(data["sizes"]),
                            }
                            agg = {k: data[k] for k in
                                   ("colors", "bgs", "fonts", "sizes", "weights", "radii")}
                            state["desktop"][name] = {"record": record, "agg": agg}
                            state["emails"] = sorted(
                                set(state["emails"]) | set(data["emails"]))
                            state["phones"] = sorted(
                                set(state["phones"]) | set(data["phones"]))
                            state["vars"].update(data["cssVars"])
                            state["font_links"] = sorted(
                                set(state["font_links"]) | set(data["fontLinks"]))
                            state["icon_font_links"] = sorted(
                                set(state["icon_font_links"]) | set(data["iconFonts"]))
                        else:
                            state["breakpoints"].setdefault(name, {})[vp_name] = {
                                k: (v and {kk: v[kk] for kk in
                                           ("font_size", "line_height", "padding", "width")})
                                for k, v in data["elements"].items()
                            }
                        save_state(state)
                    except Exception as e:  # noqa: BLE001
                        print(f"   ! page failed ({tag}): {e}")
                        state["failures"].append(f"page:{tag}")
                        save_state(state)
                await ctx.close()
        finally:
            await browser.close()


async def main():
    (OUT / "screenshots").mkdir(parents=True, exist_ok=True)
    (OUT / "html").mkdir(parents=True, exist_ok=True)

    state = load_state()
    print(f"resume: {len(state['desktop'])}/12 desktop pages already extracted, "
          f"{free_mb()} MB free")

    if artifacts_complete(state):
        print("all artifacts complete — assembling tokens.json only (no navigation)")
    else:
        await capture_all(state)

    # ---- assemble the final tokens.json exactly as the original script does ----
    agg = {k: Counter() for k in ("colors", "bgs", "fonts", "sizes", "weights", "radii")}
    for d in state["desktop"].values():
        for k in agg:
            agg[k].update(d["agg"][k])
    result = {
        "pages": {name: d["record"] for name, d in state["desktop"].items()},
        "font_links": state["font_links"],
        "icon_font_links": state["icon_font_links"],
        "breakpoints": state["breakpoints"],
        "elementor_global_vars": dict(sorted(state["vars"].items())),
        "site_wide": {k: agg[k].most_common(25) for k in agg},
        "contact": {"emails": state["emails"], "phones": state["phones"]},
    }
    (OUT / "tokens.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

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

    if state["failures"]:
        print(f"\nDONE WITH FAILURES: {len(state['failures'])} -> {state['failures']}")
        sys.exit(2)
    print(f"\nDone. {free_mb()} MB free. See {OUT}/tokens_summary.md and {OUT}/screenshots/")


if __name__ == "__main__":
    asyncio.run(main())
