---
kind: external_dependency
name: Django 5.2 LTS — project framework
slug: django
category: external_dependency
category_hints:
    - framework_behavior
scope:
    - '**'
---


Integration shape: apps live under `apps/` (`core`, `team`, `units`, `news`, `gallery`, `contact`); templates under `templates/`; static via WhiteNoise; admin via django-unfold. HTMX SPA behaviour is wired on `<body hx-boost="true">` in `base.html` so only `#main` swaps on navigation.