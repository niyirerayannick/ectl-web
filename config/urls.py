"""URL configuration for the Energicotel site (CLAUDE.md §3)."""

from django.contrib import admin
from django.urls import path

from apps.core.views import HomeView

admin.site.site_header = "Energicotel PLC administration"
admin.site.site_title = "Energicotel admin"
admin.site.index_title = "Content management"

urlpatterns = [
    path("admin/", admin.site.urls),
    # Phase 1 scaffold placeholder — the real home page lands in Phase 4
    # (CLAUDE.md §4.1); the rest of the sitemap follows the same pattern.
    path("", HomeView.as_view(), name="home"),
]

handler404 = "apps.core.views.page_not_found"
handler500 = "apps.core.views.server_error"
