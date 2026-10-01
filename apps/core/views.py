"""Core views (home page and future site-wide views)."""

from django.views.generic import TemplateView
from django.shortcuts import render


class HomeView(TemplateView):
    """Phase 1 scaffold placeholder.

    The real home view (hero slider, about collage, values, business units,
    partners) is built in Phase 4 per CLAUDE.md §4.1.
    """

    template_name = "core/home.html"


def page_not_found(request, exception):
    """Render the branded not-found page."""
    return render(request, "errors/404.html", status=404)


def server_error(request):
    """Render the branded server-error page."""
    return render(request, "errors/500.html", status=500)
