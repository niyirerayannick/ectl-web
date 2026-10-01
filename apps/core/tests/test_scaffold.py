"""Phase 1 smoke tests: the scaffold boots and the stack is wired up (CLAUDE.md §9)."""

import pytest
from django.conf import settings
from django.test import TestCase
from django.urls import reverse


class TestHomeView(TestCase):
    def test_home_url_reverses(self):
        assert reverse("home") == "/"

    def test_home_page_renders(self):
        response = self.client.get(reverse("home"))
        assert response.status_code == 200
        assert b"Phase 1" in response.content

    def test_home_page_links_built_css(self):
        response = self.client.get(reverse("home"))
        assert b"/static/css/styles.css" in response.content

    def test_home_page_loads_vendored_js(self):
        response = self.client.get(reverse("home"))
        assert b"/static/js/vendor/htmx.min.js" in response.content
        assert b"/static/js/vendor/alpine.min.js" in response.content

    def test_htmx_request_header_is_recognised(self):
        # HtmxMiddleware annotates the request; the page renders either way.
        response = self.client.get(reverse("home"), headers={"HX-Request": "true"})
        assert response.status_code == 200


class TestAdmin(TestCase):
    def test_admin_login_page_renders(self):
        response = self.client.get("/admin/login/")
        assert response.status_code == 200


@pytest.mark.django_db
def test_third_party_stack_installed():
    expected = ("unfold", "django_htmx", "template_partials", "django_tailwind_cli")
    for app in expected:
        assert app in settings.INSTALLED_APPS


@pytest.mark.django_db
def test_project_apps_installed():
    expected = (
        "apps.core",
        "apps.team",
        "apps.units",
        "apps.news",
        "apps.gallery",
        "apps.contact",
    )
    for app in expected:
        assert app in settings.INSTALLED_APPS


@pytest.mark.django_db
def test_htmx_middleware_enabled():
    assert "django_htmx.middleware.HtmxMiddleware" in settings.MIDDLEWARE
