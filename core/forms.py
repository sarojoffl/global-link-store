from django import forms

from .models import ContactMessage, NewsletterSubscriber


class ContactForm(forms.ModelForm):
    # Simple honeypot field to reduce spam bots.
    bot_field = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Your name"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com"}),
            "phone": forms.TextInput(attrs={"placeholder": "+977-98xxxxxxx (optional)"}),
            "subject": forms.TextInput(attrs={"placeholder": "Subject"}),
            "message": forms.Textarea(attrs={"rows": 6, "placeholder": "Write your message"}),
        }

    def clean_bot_field(self):
        # If bots fill this, treat as spam.
        value = (self.cleaned_data.get("bot_field") or "").strip()
        if value:
            raise forms.ValidationError("Invalid submission.")
        return value


class NewsletterForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "placeholder": "Enter your email",
            "inputmode": "email",
            "autocomplete": "email",
        }),
    )

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()

