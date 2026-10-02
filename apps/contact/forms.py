"""Accessible contact form with a honeypot field."""

from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(max_length=120, label="Your name")
    email = forms.EmailField(label="Email address")
    subject = forms.CharField(max_length=180)
    message = forms.CharField(required=False, widget=forms.Textarea)
    website = forms.CharField(required=False, widget=forms.HiddenInput)
