"""Curated team pages for the board and senior management."""

from django.views.generic import TemplateView

from apps.core.views import HtmxFragmentMixin

PEOPLE = {
	"board": [
		{"name": "Felicien MUVUNYI", "role": "Chairman", "image": "media/felicien-muvunyi.webp"},
		{"name": "Ferdy TURASENGA", "role": "Executive Director", "image": "media/ferdy-turasenga.webp"},
		{"name": "Lena Militisi Muhongerwa", "role": "Board Member", "image": "media/lena-muhongerwa.webp"},
		{"name": "Prof Josiah Lange Munda", "role": "Board Member", "image": "media/josiah-munda.webp"},
		{"name": "Silvie Kayitesi Kanimba", "role": "Board Member", "image": "media/silvie-kanimba.webp"},
		{"name": "Justin MUDAKIKWA", "role": "Board Member", "image": "media/justin-mudakikwa.webp"},
	],
	"management": [
		{"name": "Pascaline UMUTESI", "role": "Company Secretary", "image": "media/pascaline-umutesi.webp"},
		{"name": "Blaise MUNYEMANA", "role": "Director of Research and Consultancy", "image": "media/blaise-munyemana.webp"},
		{"name": "Honore MUGIRANEZA", "role": "Coordinator of Operations and Management", "image": "media/honore-mugiraneza.webp"},
		{"name": "Sam KAGORORA", "role": "Director of Administration and Finance", "image": "media/sam-kagorora.webp"},
	],
}


class PeopleView(HtmxFragmentMixin, TemplateView):
	template_name = "team/people.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		group = self.kwargs["group"]
		context.update(group=group, people=PEOPLE[group], title="Board Members" if group == "board" else "Senior Management")
		return context
