"""Contact requests submitted through the public enquiry form."""

from django.db import models


class ContactMessage(models.Model):
	name = models.CharField(max_length=120)
	email = models.EmailField()
	subject = models.CharField(max_length=180)
	message = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	handled = models.BooleanField(default=False)

	class Meta:
		ordering = ("-created_at",)

	def __str__(self):
		return f"{self.subject} from {self.name}"
