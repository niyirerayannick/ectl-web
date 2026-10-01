---
kind: external_dependency
name: Playwright + Chromium — design-reference extraction tooling
slug: playwright-chromium
category: external_dependency
category_hints:
    - framework_behavior
scope:
    - '**'
---

Used only during Phase 0 to capture the live WordPress site (https://www.energicotel.com) into `design_reference/`: 36 screenshots across desktop/tablet/mobile viewports, 12 HTML dumps, and `tokens.json` / `tokens_summary.md`. Not a runtime dependency — installed separately via `pip install playwright && playwright install chromium` before running `extract_design_tokens.py`. The script crashed mid-run when disk space was exhausted, which is why a resume helper (`resume_extract.py`) was written to skip already-valid artifacts.