"""
Base Django settings shared by every environment (CLAUDE.md §1, §6).

Environment-specific values live in ``dev.py`` and ``prod.py``. Design values
(colours, fonts, type scale, spacing) do NOT live here — they live in the
Tailwind v4 ``@theme`` block in ``theme/static_src/src/styles.css`` and are
filled in Phase 2 from ``design_reference/tokens.json`` (CLAUDE.md §5).
"""

import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

# config/settings/base.py -> config/settings -> config -> project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load a local .env file when present. Real environment variables always win.
load_dotenv(BASE_DIR / ".env")

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------

SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-dev-only-key-change-me")

# dev.py overrides to True; prod.py requires a real SECRET_KEY from the environment.
DEBUG = False

ALLOWED_HOSTS = [host.strip() for host in os.environ.get("ALLOWED_HOSTS", "").split(",") if host.strip()]

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    # django-unfold must be listed before django.contrib.admin to theme it.
    "unfold",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party (CLAUDE.md §1)
    "django_htmx",
    "template_partials",
    "django_tailwind_cli",
    # Project apps (CLAUDE.md §6)
    "apps.core",
    "apps.team",
    "apps.units",
    "apps.news",
    "apps.gallery",
    "apps.contact",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise must sit directly after SecurityMiddleware.
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Exposes request.htmx to views and templates (CLAUDE.md §7).
    "django_htmx.middleware.HtmxMiddleware",
]

ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # Exposes the site_contact dict; Phase 3 replaces it with the
                # SiteSettings singleton model (CLAUDE.md §3, §4.1).
                "apps.core.context_processors.site",
            ],
        },
    },
]

# ---------------------------------------------------------------------------
# Database — PostgreSQL via DATABASE_URL, SQLite fallback in development
# ---------------------------------------------------------------------------

_DATABASE_URL = os.environ.get("DATABASE_URL")

if _DATABASE_URL:
    DATABASES = {"default": dj_database_url.parse(_DATABASE_URL)}
else:
    # No DATABASE_URL: fall back to SQLite so development needs no server.
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "var" / "db.sqlite3",
        }
    }

# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# Internationalisation
# ---------------------------------------------------------------------------

LANGUAGE_CODE = "en"
TIME_ZONE = "Africa/Kigali"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static files (WhiteNoise) and Tailwind CSS v4 (django-tailwind-cli)
# ---------------------------------------------------------------------------

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# The first entry receives the Tailwind build output (django-tailwind-cli
# resolves TAILWIND_CLI_DIST_CSS against STATICFILES_DIRS[0]); the second holds
# hand-written assets such as the vendored HTMX/Alpine scripts.
STATICFILES_DIRS = [
    BASE_DIR / "theme" / "static_src" / "dist",
    BASE_DIR / "static",
]

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    # Compressed, content-hashed filenames in production; dev.py swaps in the
    # plain staticfiles storage so unbuilt assets keep stable URLs.
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# django-tailwind-cli — Tailwind CSS v4 via the standalone CLI (no Node.js).
# The source file is ours: the package creates it once if missing and never
# overwrites it afterwards.
TAILWIND_CLI_SRC_CSS = BASE_DIR / "theme" / "static_src" / "src" / "styles.css"
# Relative to STATICFILES_DIRS[0] -> theme/static_src/dist/css/styles.css,
# served as /static/css/styles.css through the {% tailwind_css %} template tag.
TAILWIND_CLI_DIST_CSS = "css/styles.css"
# Pin the CLI version so builds are reproducible; the binary (git-ignored) is
# cached in .django_tailwind_cli/ and only re-downloaded on a version bump.
TAILWIND_CLI_VERSION = "4.3.3"

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
