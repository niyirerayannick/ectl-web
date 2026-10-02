"""Legacy WordPress URL handling for the migration."""

from urllib.parse import urlencode, urlsplit

from django.http import HttpResponse, HttpResponsePermanentRedirect
from django.urls import reverse

from apps.core.media_assets import PARTNER_MEDIA, REFERENCE_MEDIA

LEGACY_PAGE_REDIRECTS = {
	"9": "/about/",
	"1035": "/about/board/",
	"2242": "/about/management/",
	"2501": "/business-units/power/",
	"2499": "/business-units/gas/",
	"2505": "/business-units/engineering/",
	"2503": "/business-units/solar/",
	"1040": "/gallery/",
	"12": "/contact/",
}

LEGACY_POST_REDIRECTS = {
	2734: "/news/ectl-lists-oversubscribed-corporate-bond-rse/",
	2719: "/news/ectl-showcases-its-commitment-to-sustainable-energy-at-epd-week-2024/",
}

SPAM_POST_IDS = frozenset(range(3368, 3388))


def _legacy_media_redirects():
	return {
		f"/wp-content/uploads/{source_path}": f"/static/media/{name}.webp"
		for name, source_path in {**REFERENCE_MEDIA, **PARTNER_MEDIA}.items()
	}


LEGACY_MEDIA_REDIRECTS = _legacy_media_redirects()


class LegacyWordPressRedirectMiddleware:
	"""Redirect known WordPress URLs and retire spam or executable endpoints."""

	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		path = request.path
		normalized_path = path.lower()

		if (
			normalized_path.startswith("/wp-admin")
			or normalized_path == "/wp-login.php"
			or normalized_path == "/xmlrpc.php"
			or (normalized_path.startswith("/wp-content/") and normalized_path.endswith(".php"))
		):
			return HttpResponse(status=410)

		if path in LEGACY_MEDIA_REDIRECTS:
			return HttpResponsePermanentRedirect(LEGACY_MEDIA_REDIRECTS[path])

		page_id = request.GET.get("page_id")
		if page_id == "11":
			paged = request.GET.get("paged")
			target = reverse("news-list")
			if paged and paged.isdecimal() and int(paged) > 1:
				target = f"{target}?{urlencode({'page': int(paged)})}"
			return HttpResponsePermanentRedirect(target)
		if page_id in LEGACY_PAGE_REDIRECTS:
			return HttpResponsePermanentRedirect(LEGACY_PAGE_REDIRECTS[page_id])

		post_id = request.GET.get("p")
		if post_id is not None:
			if post_id.isdecimal() and int(post_id) in LEGACY_POST_REDIRECTS:
				return HttpResponsePermanentRedirect(LEGACY_POST_REDIRECTS[int(post_id)])
			return HttpResponse(status=410)

		return self.get_response(request)