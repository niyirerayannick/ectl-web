from datetime import datetime
from urllib.parse import urlencode

from django.conf import settings
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone

from apps.core.legacy_redirects import LEGACY_MEDIA_REDIRECTS, LEGACY_PAGE_REDIRECTS
from apps.news.admin import PostAdminForm
from apps.news.models import Post


class LegacyRedirectTests(SimpleTestCase):
	def test_each_legacy_page_url_redirects_permanently(self):
		for page_id, target in LEGACY_PAGE_REDIRECTS.items():
			with self.subTest(page_id=page_id):
				response = self.client.get(f"/?page_id={page_id}")
				self.assertEqual(response.status_code, 301)
				self.assertEqual(response["Location"], target)

	def test_news_legacy_pagination_redirects_to_new_page_parameter(self):
		for paged, target in ((None, "/news/"), ("2", "/news/?page=2"), ("5", "/news/?page=5")):
			with self.subTest(paged=paged):
				query = {"page_id": "11"}
				if paged:
					query["paged"] = paged
				response = self.client.get(f"/?{urlencode(query)}")
				self.assertEqual(response.status_code, 301)
				self.assertEqual(response["Location"], target)

	def test_approved_post_urls_redirect_permanently(self):
		redirects = {
			"2734": "/news/ectl-lists-oversubscribed-corporate-bond-rse/",
			"2719": "/news/ectl-showcases-its-commitment-to-sustainable-energy-at-epd-week-2024/",
		}
		for post_id, target in redirects.items():
			with self.subTest(post_id=post_id):
				response = self.client.get(f"/?p={post_id}")
				self.assertEqual(response.status_code, 301)
				self.assertEqual(response["Location"], target)

	def test_every_known_spam_post_url_returns_gone(self):
		for post_id in range(3368, 3388):
			with self.subTest(post_id=post_id):
				self.assertEqual(self.client.get(f"/?p={post_id}").status_code, 410)

	def test_other_unapproved_post_ids_return_gone(self):
		for post_id in (1, 3361, 999999):
			with self.subTest(post_id=post_id):
				self.assertEqual(self.client.get(f"/?p={post_id}").status_code, 410)

	def test_wordpress_executable_and_admin_paths_return_gone(self):
		paths = (
			"/wp-admin/", "/wp-admin/index.php", "/wp-login.php", "/xmlrpc.php",
			"/wp-content/uploads/shell.php", "/wp-content/plugins/injected.php",
		)
		for path in paths:
			with self.subTest(path=path):
				self.assertEqual(self.client.get(path).status_code, 410)

	def test_each_curated_wordpress_upload_redirects_to_local_media(self):
		for old_path, new_path in LEGACY_MEDIA_REDIRECTS.items():
			with self.subTest(old_path=old_path):
				response = self.client.get(old_path)
				self.assertEqual(response.status_code, 301)
				self.assertEqual(response["Location"], new_path)


class SeoEndpointTests(TestCase):
	def setUp(self):
		self.post = Post.objects.create(
			wp_id=2734,
			title="ECTL lists corporate bond",
			slug="ectl-lists-oversubscribed-corporate-bond-rse",
			excerpt="Investor relations update.",
			body="<p>Bond announcement.</p>",
			cover="media/bond-listing.webp",
			cover_alt="ECTL bond listing event",
			published_at=timezone.make_aware(datetime(2026, 1, 30, 10, 0)),
		)
		Post.objects.create(
			wp_id=3368,
			title="Injected spam",
			slug="injected-spam",
			excerpt="Must not be listed.",
			published_at=timezone.make_aware(datetime(2026, 1, 30, 10, 0)),
		)

	def test_sitemap_includes_public_pages_and_only_allowlisted_news(self):
		response = self.client.get(reverse("sitemap"))
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response["Content-Type"], "application/xml; charset=utf-8")
		self.assertContains(response, f"{settings.SITE_URL}/business-units/power/")
		self.assertContains(response, f"{settings.SITE_URL}/news/{self.post.slug}/")
		self.assertNotContains(response, "/news/injected-spam/")

	def test_robots_txt_points_to_sitemap_and_disallows_wordpress_paths(self):
		response = self.client.get(reverse("robots"))
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response["Content-Type"], "text/plain; charset=utf-8")
		self.assertContains(response, f"Sitemap: {settings.SITE_URL}/sitemap.xml")
		self.assertContains(response, "Disallow: /wp-admin")
		self.assertContains(response, "Disallow: /wp-content/")

	def test_pages_render_canonical_open_graph_description_and_organization_jsonld(self):
		response = self.client.get(reverse("news-detail", args=[self.post.slug]))
		self.assertContains(response, f'<link rel="canonical" href="{settings.SITE_URL}/news/{self.post.slug}/">', html=False)
		self.assertContains(response, 'property="og:type" content="article"', html=False)
		self.assertContains(response, 'property="og:title" content="ECTL lists corporate bond"', html=False)
		self.assertContains(response, 'name="description" content="Investor relations update."', html=False)
		self.assertContains(response, 'type="application/ld+json"', html=False)
		self.assertContains(response, '"@type":"Organization"', html=False)
		self.assertContains(response, 'alt="ECTL bond listing event"', html=False)


class PostAltTextAdminTests(TestCase):
	def test_cover_alt_is_required_when_cover_is_set(self):
		form = PostAdminForm(data={"cover": "media/cover.webp", "cover_alt": "", "body": ""})
		self.assertFalse(form.is_valid())
		self.assertIn("cover_alt", form.errors)

	def test_inline_image_requires_nonempty_alt_text(self):
		for body in ('<p><img src="image.webp"></p>', '<img src="image.webp" alt=" ">'):
			with self.subTest(body=body):
				form = PostAdminForm(data={"cover": "", "cover_alt": "", "body": body})
				self.assertFalse(form.is_valid())
				self.assertIn("body", form.errors)

	def test_valid_cover_and_inline_alt_text_pass_validation(self):
		form = PostAdminForm(data={
			"wp_id": 12345,
			"title": "Valid title",
			"slug": "valid-title",
			"excerpt": "",
			"body": '<p><img src="image.webp" alt="Hydropower facility"></p>',
			"cover": "media/cover.webp",
			"cover_alt": "Hydropower facility",
			"published_at": "2026-01-30 10:00:00",
			"status": "publish",
			"category": "Corporate News",
		})
		self.assertTrue(form.is_valid(), form.errors)