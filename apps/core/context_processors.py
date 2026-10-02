"""Site-wide template context (CLAUDE.md §3).

Phase 3 replaces these constants with the ``SiteSettings`` singleton model.
Keep the shape of the dict stable so templates do not need to change.
"""

from django.conf import settings
from django.templatetags.static import static
from django.urls import reverse

from apps.news.models import Post

# TODO(Phase 3): emails come from design_reference/tokens.json -> contact.emails
# and all values move into SiteSettings (one canonical address, §2.3).
_SITE_CONTACT = {
    "phones": ["(+250) 786 420 337", "(+250) 788 207 637"],
    "emails": [],
    "address": "Gasabo – Gacuriro, KG 436 St, Plot No. 6A, Kigali",
    "hours": "Mon–Fri 9:00 AM – 5:00 PM",
}


def site(request):
    return {"site_contact": _SITE_CONTACT}


PAGE_METADATA = {
    "home": ("Energicotel PLC", "Energicotel PLC develops renewable energy and engineering projects in Rwanda and across the region."),
    "about": ("About Energicotel PLC", "Learn about Energicotel PLC, its mission, values, and renewable energy operations."),
    "board": ("Board Members", "Meet the Board Members guiding Energicotel PLC."),
    "management": ("Senior Management", "Meet the senior management team at Energicotel PLC."),
    "unit-detail": ("Business Units", "Explore Energicotel PLC's energy and engineering business units."),
    "news-list": ("News and Events", "Read corporate news, investor updates, and events from Energicotel PLC."),
    "news-detail": ("Energicotel PLC News", "Read the latest news and updates from Energicotel PLC."),
    "gallery": ("Gallery", "View Energicotel PLC projects, energy infrastructure, and events."),
    "contact": ("Contact Energicotel PLC", "Contact Energicotel PLC about energy, engineering, and project enquiries."),
}


def seo(request):
    match = getattr(request, "resolver_match", None)
    route_name = match.url_name if match else "home"
    title, description = PAGE_METADATA.get(route_name, PAGE_METADATA["home"])
    path = request.path or "/"
    canonical_url = f"{settings.SITE_URL}{path}"
    image_url = f"{settings.SITE_URL}{static('img/Logo-Tr-01.png')}"

    if route_name == "unit-detail" and match and match.kwargs.get("slug"):
        unit = match.kwargs["slug"].replace("-", " ").title()
        title = f"ECTL {unit}"
        description = f"Learn about Energicotel PLC's {title} services, projects, and capabilities."
    elif route_name == "news-detail" and match and match.kwargs.get("slug"):
        post = Post.objects.filter(
            slug=match.kwargs["slug"], status="publish", wp_id__in=(2734, 2719)
        ).first()
        if post:
            title = post.title
            description = (post.excerpt or post.title)[:300]
            if post.cover:
                image_url = f"{settings.SITE_URL}{static(post.cover)}"

    organization = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Energicotel PLC",
        "url": f"{settings.SITE_URL}/",
        "logo": image_url,
        "telephone": _SITE_CONTACT["phones"][0],
        "contactPoint": [
            {"@type": "ContactPoint", "telephone": phone, "contactType": "customer service"}
            for phone in _SITE_CONTACT["phones"]
        ],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "KG 436 St, Plot No. 6A, Gacuriro",
            "addressLocality": "Kigali",
            "addressCountry": "RW",
        },
    }
    return {
        "seo_title": title,
        "seo_description": description,
        "canonical_url": canonical_url,
        "og_image_url": image_url,
        "organization_jsonld": organization,
    }
