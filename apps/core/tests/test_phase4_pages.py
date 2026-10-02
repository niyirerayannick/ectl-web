from datetime import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.news.models import Post


class PhaseFourPagesTests(TestCase):
    def setUp(self):
        published_at = timezone.make_aware(datetime(2026, 1, 30, 10, 0))
        self.bond = Post.objects.create(
            wp_id=2734,
            title="ECTL lists corporate bond",
            slug="ectl-lists-oversubscribed-corporate-bond-rse",
            excerpt="An ECTL corporate bond announcement.",
            body="<p>Investor relations update.</p>",
            cover="media/bond-listing.webp",
            published_at=published_at,
        )
        Post.objects.create(
            wp_id=3361,
            title="De juiste route kiezen bij problemen",
            slug="de-juiste-route-kiezen-bij-problemen",
            excerpt="Unrelated injected copy.",
            body="<p>Unrelated content.</p>",
            published_at=published_at,
        )
        for wp_id in range(3368, 3388):
            Post.objects.create(
                wp_id=wp_id,
                title=f"Betting post {wp_id}",
                slug=f"betting-post-{wp_id}",
                excerpt="Sports betting content.",
                body="<p>Betting.</p>",
                published_at=published_at,
            )

    def test_requested_page_routes_render(self):
        paths = [
            reverse("home"),
            reverse("about"),
            reverse("board"),
            reverse("management"),
            reverse("news-list"),
            reverse("news-detail", args=[self.bond.slug]),
            reverse("gallery"),
            reverse("contact"),
        ] + [reverse("unit-detail", args=[slug]) for slug in ("power", "gas", "engineering", "solar")]
        for path in paths:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)

    def test_news_list_and_detail_exclude_unapproved_injected_ids(self):
        response = self.client.get(reverse("news-list"))
        self.assertContains(response, "ECTL lists corporate bond")
        self.assertNotContains(response, "De juiste route kiezen")
        self.assertNotContains(response, "Betting post")
        self.assertEqual(self.client.get(reverse("news-detail", args=["de-juiste-route-kiezen-bij-problemen"])).status_code, 404)

    def test_valid_contact_message_is_saved(self):
        response = self.client.post(reverse("contact"), {
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Project enquiry",
            "message": "Please contact me.",
            "website": "",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your message has been received")
