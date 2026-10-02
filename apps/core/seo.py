"""Sitemap and robots.txt endpoints."""

from types import SimpleNamespace
from urllib.parse import urlsplit
from xml.sax.saxutils import escape

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.http import HttpResponse
from django.urls import reverse

from apps.news.models import Post


class StaticPagesSitemap(Sitemap):
	priority = 0.7
	changefreq = "monthly"

	def items(self):
		return (
			"home", "about", "board", "management", "unit-detail-power", "unit-detail-gas",
			"unit-detail-engineering", "unit-detail-solar", "news-list", "gallery", "contact",
		)

	def location(self, item):
		if item.startswith("unit-detail-"):
			return reverse("unit-detail", kwargs={"slug": item.removeprefix("unit-detail-")})
		return reverse(item)


class NewsSitemap(Sitemap):
	changefreq = "yearly"
	priority = 0.6

	def items(self):
		return Post.objects.filter(status="publish", wp_id__in=(2734, 2719))

	def lastmod(self, item):
		return item.published_at

	def location(self, item):
		return reverse("news-detail", kwargs={"slug": item.slug})


def sitemap_index(request):
	"""Render the Django sitemap using the configured canonical site domain."""
	site = SimpleNamespace(domain=urlsplit(settings.SITE_URL).netloc)
	protocol = urlsplit(settings.SITE_URL).scheme
	urls = []
	for sitemap_class in (StaticPagesSitemap, NewsSitemap):
		urls.extend(sitemap_class().get_urls(site=site, protocol=protocol))

	entries = []
	for item in urls:
		lastmod = f"<lastmod>{item['lastmod'].isoformat()}</lastmod>" if item.get("lastmod") else ""
		entries.append(
			"<url><loc>{}</loc>{}</url>".format(escape(item["location"]), lastmod)
		)
	content = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{}</urlset>'.format("".join(entries))
	return HttpResponse(content, content_type="application/xml; charset=utf-8")


def robots_txt(request):
	content = "User-agent: *\nAllow: /\nDisallow: /wp-admin\nDisallow: /wp-login.php\nDisallow: /xmlrpc.php\nDisallow: /wp-content/\nSitemap: {}/sitemap.xml\n".format(settings.SITE_URL.rstrip("/"))
	return HttpResponse(content, content_type="text/plain; charset=utf-8")