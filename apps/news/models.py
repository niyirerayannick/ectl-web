"""Editorial content imported from the tightly allow-listed WordPress set."""

from django.db import models


class Post(models.Model):
	wp_id = models.PositiveIntegerField(unique=True)
	title = models.CharField(max_length=300)
	slug = models.SlugField(max_length=220, unique=True)
	excerpt = models.TextField(blank=True)
	body = models.TextField(blank=True)
	cover = models.CharField(max_length=300, blank=True)
	cover_alt = models.CharField(max_length=300, blank=True)
	published_at = models.DateTimeField()
	status = models.CharField(max_length=20, default="publish")
	category = models.CharField(max_length=100, default="Corporate News")

	class Meta:
		ordering = ("-published_at", "title")

	def __str__(self):
		return self.title
