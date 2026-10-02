"""Editorial administration with required alternative text for post imagery."""

from html.parser import HTMLParser

from django import forms
from django.contrib import admin

from apps.news.models import Post


class _ImageAltParser(HTMLParser):
	def __init__(self):
		super().__init__()
		self.missing_alt = False

	def handle_starttag(self, tag, attrs):
		if tag.lower() != "img":
			return
		attributes = dict(attrs)
		if not attributes.get("alt", "").strip():
			self.missing_alt = True


class PostAdminForm(forms.ModelForm):
	class Meta:
		model = Post
		fields = "__all__"

	def clean(self):
		cleaned_data = super().clean()
		if cleaned_data.get("cover") and not cleaned_data.get("cover_alt", "").strip():
			self.add_error("cover_alt", "Alternative text is required when a cover image is set.")

		parser = _ImageAltParser()
		parser.feed(cleaned_data.get("body", ""))
		if parser.missing_alt:
			self.add_error("body", "Every image in the post body must have non-empty alternative text.")
		return cleaned_data


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
	form = PostAdminForm
	list_display = ("title", "category", "published_at", "status", "wp_id")
	list_filter = ("status", "category")
	search_fields = ("title", "excerpt", "body")
	prepopulated_fields = {"slug": ("title",)}
