from django import forms

from accounts.models import Address


class CheckoutForm(forms.Form):
    address_id = forms.ModelChoiceField(
        queryset=Address.objects.none(),
        required=False,
        label="Saved address",
        empty_label="Enter a new address",
    )
    full_name = forms.CharField(max_length=120)
    phone = forms.CharField(max_length=20)
    email = forms.EmailField()
    street = forms.CharField(max_length=255, label="Street address")
    city = forms.CharField(max_length=100)
    province = forms.CharField(max_length=100, required=False)
    postal_code = forms.CharField(max_length=20, required=False, label="Postal code")
    payment_method = forms.ChoiceField(
        choices=[
            ("cod", "Cash on Delivery"),
            ("bank", "Bank Transfer"),
        ],
        widget=forms.RadioSelect,
        initial="cod",
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3}),
        required=False,
        label="Order notes (optional)",
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        input_class = {"class": "shop-input"}
        for name in (
            "full_name", "phone", "email", "street", "city",
            "province", "postal_code", "notes",
        ):
            if name in self.fields:
                self.fields[name].widget.attrs.update(input_class)
        self.fields["address_id"].widget.attrs.update(input_class)
        self.fields["address_id"].queryset = Address.objects.filter(user=user)
        if user.email:
            self.fields["email"].initial = user.email
        if hasattr(user, "profile") and user.profile.phone:
            self.fields["phone"].initial = user.profile.phone
        default = Address.objects.filter(user=user, is_default=True).first()
        if default:
            self.fields["address_id"].initial = default.pk
            self._apply_address(default)

    def _apply_address(self, address):
        self.fields["full_name"].initial = address.full_name
        self.fields["phone"].initial = address.phone
        self.fields["street"].initial = address.street
        self.fields["city"].initial = address.city
        self.fields["province"].initial = address.province
        self.fields["postal_code"].initial = address.postal_code

    def clean(self):
        cleaned = super().clean()
        address = cleaned.get("address_id")
        if address:
            cleaned["full_name"] = address.full_name
            cleaned["phone"] = address.phone
            cleaned["street"] = address.street
            cleaned["city"] = address.city
            cleaned["province"] = address.province
            cleaned["postal_code"] = address.postal_code
        return cleaned
