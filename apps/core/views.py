"""Core views (home page and future site-wide views)."""

from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Phase 1 scaffold placeholder.

    The real home view (hero slider, about collage, values, business units,
    partners) is built in Phase 4 per CLAUDE.md §4.1.
    """

    template_name = "core/home.html"
