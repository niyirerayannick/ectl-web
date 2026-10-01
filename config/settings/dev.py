"""
Development settings (manage.py defaults to this module).

Runs with the SQLite fallback (``var/db.sqlite3``) when DATABASE_URL is unset,
serves static files straight from their source directories, and prints emails
to the console.
"""

from .base import *  # noqa: F401,F403

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", *ALLOWED_HOSTS]

# Serve static files straight from STATICFILES_DIRS and app static folders,
# so no collectstatic run is needed during development.
WHITENOISE_USE_FINDERS = True

# Keep plain (unhashed) static URLs in development.
STORAGES = {
    **STORAGES,
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

# Contact-form mails are printed to the runserver console (Phase 4+).
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {"handlers": ["console"], "level": "WARNING"},
}
