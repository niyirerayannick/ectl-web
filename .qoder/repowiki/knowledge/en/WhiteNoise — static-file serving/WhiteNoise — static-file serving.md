---
kind: external_dependency
name: WhiteNoise — static-file serving
slug: whitenoise
category: external_dependency
category_hints:
    - framework_behavior
scope:
    - '**'
---

WhiteNoise 6.12 serves static files in both development and production (behind Gunicorn/Nginx). In dev it warns once about a missing `staticfiles/` directory until the first `collectstatic`; this is cosmetic and documented in the README.