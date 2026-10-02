"""Core views (home page and future site-wide views)."""

from django.views.generic import TemplateView
from django.shortcuts import render

from apps.core.content import ABOUT_COPY, ABOUT_IMAGES, CORE_VALUES, HERO_SLIDES, PARTNERS, STATS
from apps.units.content import UNITS


class HtmxFragmentMixin:
    """Use a named template partial for HTMX requests while keeping full-page HTML intact."""

    partial_name = "main"

    def get_template_names(self):
        names = super().get_template_names()
        try:
            request = self.request
        except AttributeError:
            return names

        if getattr(request, "htmx", False) and not getattr(request.htmx, "history_restore_request", False):
            fragment_names = []
            for name in names:
                if "#" not in name:
                    fragment_names.append(f"{name}#{self.partial_name}")
                else:
                    fragment_names.append(name)
            return fragment_names
        return names


class HtmxTemplateView(HtmxFragmentMixin, TemplateView):
    pass


class HomeView(HtmxTemplateView):
    """Curated home page.

    The real home view (hero slider, about collage, values, business units,
    partners) is built in Phase 4 per CLAUDE.md §4.1.
    """

    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            about_copy=ABOUT_COPY,
            about_images=ABOUT_IMAGES,
            values=CORE_VALUES,
            slides=HERO_SLIDES,
            partners=PARTNERS,
            unit_list=UNITS,
        )
        return context


class AboutView(HtmxTemplateView):
    """Curated about page.

    The real about view (hero slider, about collage, values, business units,
    partners) is built in Phase 4 per CLAUDE.md §4.1.
    """

    template_name = "core/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            about_copy=ABOUT_COPY,
            about_images=ABOUT_IMAGES,
            values=CORE_VALUES,
            stats=STATS,
        )
        return context


def page_not_found(request, exception):
    """Render the branded not-found page."""
    return render(request, "errors/404.html", status=404)


def server_error(request):
    """Render the branded server-error page."""
    return render(request, "errors/500.html", status=500)
