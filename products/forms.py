from django import forms

from .models import ProductReview


class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ("rating", "title", "body")
        widgets = {
            "rating": forms.HiddenInput(),
            "title": forms.TextInput(
                attrs={
                    "placeholder": "Summarize your experience",
                    "maxlength": 120,
                }
            ),
            "body": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "What did you like or dislike?",
                }
            ),
        }

    def clean_rating(self):
        rating = self.cleaned_data.get("rating")
        if rating is None or rating < 1 or rating > 5:
            raise forms.ValidationError("Please select a rating from 1 to 5 stars.")
        return rating

    def clean_title(self):
        title = (self.cleaned_data.get("title") or "").strip()
        if len(title) < 3:
            raise forms.ValidationError("Review title must be at least 3 characters.")
        return title

    def clean_body(self):
        body = (self.cleaned_data.get("body") or "").strip()
        if len(body) < 10:
            raise forms.ValidationError("Please write at least 10 characters in your review.")
        return body
