"""Site-wide middleware for HTMX-aware cache headers and progressive enhancement."""


class HXRequestVaryMiddleware:
    """Ensure HTMX responses are not cached as a full-document page."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.headers.get("HX-Request") == "true":
            existing = response.headers.get("Vary", "")
            values = [item.strip() for item in existing.split(",") if item.strip()]
            if "HX-Request" not in values:
                values.append("HX-Request")
                response.headers["Vary"] = ", ".join(values)
        return response