from datetime import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.html import conditional_escape

from apps.news.models import Post
from apps.units.content import UNITS


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

    def test_business_unit_htmx_swap_returns_replaceable_current_unit_content(self):
        power = self.client.get(reverse("unit-detail", args=["power"]))
        gas = self.client.get(
            reverse("unit-detail", args=["gas"]),
            headers={"HX-Request": "true", "HX-Target": "unit-content"},
        )

        self.assertContains(power, "Keya Hydropower Plant")
        self.assertContains(power, 'hx-select="#unit-content"', html=False)
        self.assertEqual(gas.status_code, 200)
        self.assertNotContains(gas, "<html", html=False)
        self.assertContains(gas, '<div id="unit-content">', html=False)
        self.assertContains(gas, "ECTL Gas", html=False)
        self.assertContains(gas, "Gas distribution infrastructure", html=False)
        self.assertContains(gas, 'aria-current="page"', html=False)
        self.assertNotContains(gas, "Keya Hydropower Plant", html=False)

    def test_boosted_unit_navigation_returns_main_fragment(self):
        response = self.client.get(
            reverse("unit-detail", args=["solar"]),
            headers={"HX-Request": "true", "HX-Boosted": "true", "HX-Target": "main"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "<html", html=False)
        self.assertContains(response, '<main id="main"', html=False)
        self.assertContains(response, "ECTL Solar", html=False)
        self.assertContains(response, "Solar PV feasibility and system design", html=False)
        self.assertNotContains(response, "Keya Hydropower Plant", html=False)

    def test_boosted_top_menu_routes_return_main_fragments(self):
        routes = (
            (reverse("board"), "Felicien MUVUNYI"),
            (reverse("management"), "Pascaline UMUTESI"),
            (reverse("news-list"), "news-grid"),
            (reverse("gallery"), "gallery-tile"),
            (reverse("contact"), "Contact Energicotel"),
        )
        for path, expected_content in routes:
            with self.subTest(path=path):
                response = self.client.get(
                    path,
                    headers={"HX-Request": "true", "HX-Boosted": "true", "HX-Target": "main"},
                )
                self.assertEqual(response.status_code, 200)
                self.assertNotContains(response, "<html", html=False)
                self.assertContains(response, '<main id="main"', html=False)
                self.assertContains(response, expected_content, html=False)

    def test_unit_pages_do_not_render_dictionary_methods_as_content(self):
        for slug in ("power", "gas", "engineering", "solar"):
            with self.subTest(slug=slug):
                response = self.client.get(reverse("unit-detail", args=[slug]))
                self.assertEqual(response.status_code, 200)
                self.assertNotContains(response, "('heading',", html=False)
                self.assertNotContains(response, "('body',", html=False)
                for section in UNITS[slug]["sections"]:
                    heading = str(conditional_escape(section["heading"])).encode()
                    self.assertEqual(response.content.count(heading), 1)

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
