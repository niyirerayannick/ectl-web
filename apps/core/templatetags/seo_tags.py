"""Template filters for safely embedded SEO structured data."""

import json

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def json_ld(value):
    encoded = json.dumps(value, ensure_ascii=True, separators=(",", ":"))
    return mark_safe(encoded.replace("</", "<\\/"))
