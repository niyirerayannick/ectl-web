"""Site-wide template context (CLAUDE.md §3).

Phase 3 replaces these constants with the ``SiteSettings`` singleton model.
Keep the shape of the dict stable so templates do not need to change.
"""

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
