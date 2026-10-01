"""
Production settings (wsgi.py defaults to this module).

Required environment variables (see .env.example):
* SECRET_KEY
* ALLOWED_HOSTS
* DATABASE_URL (PostgreSQL)

Hardened defaults; ``python manage.py check --deploy`` becomes part of the
Phase 7 gate (CLAUDE.md §9).
"""

import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F401,F403

_secret_key = os.environ.get("SECRET_KEY")
if not _secret_key:
    raise ImproperlyConfigured("SECRET_KEY must be set in production (see .env.example).")
SECRET_KEY = _secret_key

if not os.environ.get("DATABASE_URL"):
    raise ImproperlyConfigured("DATABASE_URL must be set in production (PostgreSQL).")
DATABASES["default"].setdefault("CONN_MAX_AGE", 600)
DATABASES["default"].setdefault("CONN_HEALTH_CHECKS", True)

if not ALLOWED_HOSTS:
    raise ImproperlyConfigured("ALLOWED_HOSTS must be set in production.")

CSRF_TRUSTED_ORIGINS = [
    origin.strip() for origin in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if origin.strip()
]

# ---------------------------------------------------------------------------
# Hardening (tuned further in Phase 7)
# ---------------------------------------------------------------------------

# The site runs behind Nginx/Cloudflare with HTTPS (CLAUDE.md §1).
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30  # 30 days — raise after the Phase 7 sign-off
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
