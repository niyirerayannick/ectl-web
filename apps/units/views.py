"""Shared detail view for the four business units."""

from django.http import Http404
from django.views.generic import TemplateView

from apps.core.views import HtmxFragmentMixin
from apps.units.content import UNITS


class UnitDetailView(HtmxFragmentMixin, TemplateView):
	template_name = "units/detail.html"

	partial_name = "unit-content"

	def get_template_names(self):
		names = super().get_template_names()
		if self.request.htmx and not getattr(self.request.htmx, "history_restore_request", False):
			if self.request.htmx.boosted:
				return ["units/detail.html#main"]
			return ["units/detail.html#unit-content"]
		return names

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		slug = self.kwargs["slug"]
		if slug not in UNITS:
			raise Http404
		context.update(unit=UNITS[slug], units=UNITS, slug=slug)
		return context
