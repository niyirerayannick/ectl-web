"""URL configuration for the Energicotel site (CLAUDE.md §3)."""

from django.contrib import admin
from django.urls import path

from apps.core.views import AboutView, HomeView
from apps.team.views import PeopleView
from apps.units.views import UnitDetailView
from apps.news.views import NewsDetailView, NewsListView
from apps.gallery.views import GalleryView
from apps.contact.views import ContactView

admin.site.site_header = "Energicotel PLC administration"
admin.site.site_title = "Energicotel admin"
admin.site.index_title = "Content management"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomeView.as_view(), name="home"),
    path("about/", AboutView.as_view(), name="about"),
    path("about/board/", PeopleView.as_view(), {"group": "board"}, name="board"),
    path("about/management/", PeopleView.as_view(), {"group": "management"}, name="management"),
    path("business-units/<slug:slug>/", UnitDetailView.as_view(), name="unit-detail"),
    path("news/", NewsListView.as_view(), name="news-list"),
    path("news/<slug:slug>/", NewsDetailView.as_view(), name="news-detail"),
    path("gallery/", GalleryView.as_view(), name="gallery"),
    path("contact/", ContactView.as_view(), name="contact"),
]

handler404 = "apps.core.views.page_not_found"
handler500 = "apps.core.views.server_error"
