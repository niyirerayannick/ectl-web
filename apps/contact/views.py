"""Contact form view; submissions are stored even when SMTP is unavailable."""

from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from apps.core.views import HtmxFragmentMixin
from apps.contact.forms import ContactForm
from apps.contact.models import ContactMessage


class ContactView(HtmxFragmentMixin, TemplateView):
	template_name = "contact/index.html"
	partial_name = "contact-form"

	def get_template_names(self):
		names = super().get_template_names()
		if self.request.htmx and not getattr(self.request.htmx, "history_restore_request", False):
			return ["contact/index.html#contact-form"]
		return names

	def get(self, request, *args, **kwargs):
		return render(request, self.get_template_names()[0], {"form": ContactForm()})

	def post(self, request, *args, **kwargs):
		form = ContactForm(request.POST)
		success = False
		if form.is_valid():
			if form.cleaned_data["website"]:
				return render(request, self.get_template_names()[0], {"form": ContactForm(), "success": True})
			if request.session.get("contact_last_post"):
				from django.utils import timezone

				last_post = timezone.datetime.fromisoformat(request.session["contact_last_post"])
				if (timezone.now() - last_post).total_seconds() < 30:
					form.add_error(None, "Please wait before sending another message.")
				else:
					success = self._save_message(form, request)
			else:
				success = self._save_message(form, request)
		if success:
			form = ContactForm()
		return render(request, self.get_template_names()[0], {"form": form, "success": success})

	@staticmethod
	def _save_message(form, request):
		message = ContactMessage.objects.create(
			name=form.cleaned_data["name"],
			email=form.cleaned_data["email"],
			subject=form.cleaned_data["subject"],
			message=form.cleaned_data["message"],
		)
		request.session["contact_last_post"] = message.created_at.isoformat()
		try:
			send_mail(
				subject=f"ECTL website enquiry: {message.subject}",
				message=f"From: {message.name} <{message.email}>\n\n{message.message}",
				from_email=None,
				recipient_list=["energicotel@epcafrica.com"],
				fail_silently=True,
			)
		except Exception:
			pass
		return True
