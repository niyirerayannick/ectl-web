"""A curated gallery of ECTL project and event photography."""

from django.views.generic import TemplateView

from apps.core.views import HtmxFragmentMixin

GALLERY_IMAGES = [
	{"src": "media/gallery-rusumo-event.webp", "alt": "Rusumo Falls hydropower project", "caption": "Regional hydropower infrastructure"},
	{"src": "media/gallery-team-event.webp", "alt": "ECTL team at a project site", "caption": "Project team in the field"},
	{"src": "media/bond-listing.webp", "alt": "ECTL corporate bond listing event", "caption": "Corporate bond listing"},
	{"src": "media/keya-hydropower.webp", "alt": "Keya hydropower plant", "caption": "Hydropower generation"},
	{"src": "media/engineering-project.webp", "alt": "Infrastructure engineering project", "caption": "Engineering consultancy"},
	{"src": "media/solar-panels.webp", "alt": "Solar panels at an energy site", "caption": "Renewable energy"},
	{"src": "media/gallery-site-event.webp", "alt": "ECTL energy project site", "caption": "Energy infrastructure"},
	{"src": "media/gallery-project-team.webp", "alt": "Engineering team at a project", "caption": "Project delivery"},
]


class GalleryView(HtmxFragmentMixin, TemplateView):
	template_name = "gallery/index.html"
	partial_name = "gallery-grid"

	def get_template_names(self):
		names = super().get_template_names()
		if self.request.htmx and not getattr(self.request.htmx, "history_restore_request", False):
			return ["gallery/index.html#gallery-grid"]
		return names

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		page = int(self.request.GET.get("page", "1"))
		start = (page - 1) * 4
		images = GALLERY_IMAGES[start:start + 4]
		context["images"] = images
		context["page"] = page
		context["has_next"] = start + len(images) < len(GALLERY_IMAGES)
		return context
