"""Import only the explicit ECTL allow-list; never crawl WordPress listings."""

from __future__ import annotations

import io
import json
import html
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import nh3
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.utils.text import slugify
from PIL import Image

from apps.news.models import Post

ALLOWED_IDS = frozenset({2734, 2719, 3361})
ELIGIBLE_IDS = frozenset({2734, 2719})
BLOCKED_TERMS = re.compile(
    r"\b(?:bet|betting|gambl(?:e|ing)|casino|wager|odds|bookmaker|sportsbook|"
    r"paris sportifs|pari sportif|parier|pronostic|apuestas|apostas|scommesse|"
    r"wedden|weddenschappen|wett|glücksspiel)\b",
    re.IGNORECASE,
)
ALLOWED_TAGS = {"p", "strong", "em", "a", "ul", "ol", "li", "h2", "h3", "h4", "img", "figure", "figcaption", "blockquote", "br"}
ALLOWED_ATTRIBUTES = {"a": {"href", "title"}, "img": {"src", "alt", "title", "width", "height"}}
USER_AGENT = "EnergicotelMigration/1.0 (allow-listed content migration)"


def api_url(base: str, route: str) -> str:
    parsed = urllib.parse.urlparse(base)
    return urllib.parse.urlunparse((parsed.scheme, parsed.netloc, "/index.php", "", urllib.parse.urlencode({"rest_route": route}), ""))


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
        raise CommandError(f"WordPress request failed for {url}: {error}") from error
    if not isinstance(payload, dict) or "id" not in payload:
        raise CommandError(f"WordPress returned an invalid post response for {url}")
    return payload


def download_webp(url: str, destination: Path) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = response.read()
        with Image.open(io.BytesIO(data)) as source:
            source.seek(0)
            image = source.convert("RGB") if source.mode not in ("RGB", "RGBA") else source.copy()
            destination.parent.mkdir(parents=True, exist_ok=True)
            image.save(destination, "WEBP", quality=84, method=6)
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        raise CommandError(f"Could not convert content image {url}: {error}") from error
    return "media/" + destination.name


class Command(BaseCommand):
    help = "Import only approved ECTL WordPress posts (2734, 2719, 3361)."

    def add_arguments(self, parser):
        parser.add_argument("--base", default="https://www.energicotel.com")
        parser.add_argument("--ids", default="2734,2719,3361", help="Comma-separated IDs; values outside the hard allow-list are rejected.")

    def handle(self, *args, **options):
        requested_ids = [int(value.strip()) for value in options["ids"].split(",") if value.strip()]
        if not requested_ids or len(requested_ids) != len(set(requested_ids)):
            raise CommandError("Provide each allowed post ID at most once.")
        forbidden = set(requested_ids) - ALLOWED_IDS
        if forbidden:
            raise CommandError(f"Post IDs are not on the allow-list: {', '.join(map(str, sorted(forbidden)))}")

        base = options["base"].rstrip("/")
        media_root = Path(settings.BASE_DIR) / "static" / "media"
        for post_id in requested_ids:
            if post_id not in ELIGIBLE_IDS:
                self.stdout.write(self.style.WARNING(f"Skipped {post_id}: not approved as legitimate ECTL content."))
                continue
            record = fetch_json(api_url(base, f"/wp/v2/posts/{post_id}"))
            if int(record["id"]) != post_id:
                raise CommandError(f"WordPress returned ID {record['id']} for requested ID {post_id}.")
            title = html.unescape(nh3.clean(record.get("title", {}).get("rendered", ""), tags=set(), attributes={}))
            content_html = record.get("content", {}).get("rendered", "")
            plain_text = re.sub(r"<[^>]+>", " ", content_html)
            if BLOCKED_TERMS.search(title) or BLOCKED_TERMS.search(plain_text):
                self.stdout.write(self.style.ERROR(f"Skipped {post_id}: gambling/betting content detected."))
                continue

            post_slug = "ectl-lists-oversubscribed-corporate-bond-rse" if post_id == 2734 else slugify(record.get("slug") or title)[:220]
            if not post_slug:
                raise CommandError(f"Post {post_id} has no usable slug.")
            image_map = {}
            image_sources = re.findall(r'''<img\b[^>]*?src=["']([^"']+)["']''', content_html, flags=re.IGNORECASE)
            featured_id = record.get("featured_media")
            if featured_id:
                media = fetch_json(api_url(base, f"/wp/v2/media/{int(featured_id)}"))
                featured_url = media.get("source_url")
                if featured_url:
                    image_sources.insert(0, featured_url)
            for image_index, source in enumerate(dict.fromkeys(image_sources), start=1):
                if image_index == 1 and post_id == 2734:
                    safe_name = "bond-listing.webp"
                elif image_index == 1 and post_id == 2719:
                    safe_name = "epd-week-2024.webp"
                else:
                    safe_name = f"{post_slug}-image-{image_index}.webp"
                image_map[source] = download_webp(source, media_root / safe_name)

            for remote, local in image_map.items():
                content_html = content_html.replace(remote, "/static/" + local)
            body = nh3.clean(content_html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, url_schemes={"http", "https"})
            excerpt_html = record.get("excerpt", {}).get("rendered", "")
            excerpt = html.unescape(nh3.clean(excerpt_html, tags=set(), attributes={}))[:1200]
            cover = next(iter(image_map.values()), "")
            published_at = timezone.datetime.fromisoformat(record["date"].replace("Z", "+00:00"))
            if timezone.is_naive(published_at):
                published_at = timezone.make_aware(published_at, timezone.get_default_timezone())
            post, created = Post.objects.update_or_create(
                wp_id=post_id,
                defaults={
                    "title": title,
                    "slug": post_slug,
                    "excerpt": excerpt,
                    "body": body,
                    "cover": cover,
                    "published_at": published_at,
                    "status": "publish",
                    "category": "Investor Relations" if post_id == 2734 else "Corporate News",
                },
            )
            action = "Imported" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{action} {post.wp_id}: {post.title}"))
