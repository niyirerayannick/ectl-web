"""Download and convert only assets referenced by the curated Phase 4 views."""

from __future__ import annotations

import io
import urllib.error
import urllib.request
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from PIL import Image

from apps.core.media_assets import PARTNER_MEDIA, REFERENCE_MEDIA

BASE_URL = "https://www.energicotel.com/wp-content/uploads/"
USER_AGENT = "EnergicotelMigration/1.0 (curated reference media)"


class Command(BaseCommand):
    help = "Fetch only explicitly referenced page images and convert them to WebP."

    def handle(self, *args, **options):
        media_root = Path(settings.BASE_DIR) / "static" / "media"
        assets = {**REFERENCE_MEDIA, **PARTNER_MEDIA}
        failures = []
        for name, source_path in assets.items():
            destination = media_root / f"{name}.webp"
            request = urllib.request.Request(BASE_URL + source_path, headers={"User-Agent": USER_AGENT})
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    data = response.read()
                with Image.open(io.BytesIO(data)) as source:
                    source.seek(0)
                    image = source.copy()
                    if image.mode not in ("RGB", "RGBA"):
                        image = image.convert("RGB")
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    image.save(destination, "WEBP", quality=84, method=6)
            except (urllib.error.URLError, TimeoutError, OSError) as error:
                failures.append(f"{name} ({source_path}): {error}")
                continue
            self.stdout.write(f"Saved {destination.relative_to(settings.BASE_DIR)}")
        if failures:
            raise CommandError("Some selected media could not be downloaded:\n" + "\n".join(failures))
