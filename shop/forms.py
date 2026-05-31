from django import forms

from accounts.models import Address


class CheckoutForm(forms.Form):
    address_id = forms.ModelChoiceField(
        queryset=Address.objects.none(),
        required=False,
        label="Saved address",
        empty_label="Enter a new address",
    )
    shipping_area = forms.ChoiceField(
        choices=[
            ("inside_valley", "Inside Kathmandu Valley"),
            ("outside_valley", "Outside Kathmandu Valley"),
        ],
        initial="inside_valley",
        label="Shipping Area",
    )
    full_name = forms.CharField(max_length=120)
    phone = forms.CharField(max_length=20)
    email = forms.EmailField()
    street = forms.CharField(max_length=255, label="Street address")
    city = forms.CharField(max_length=100)
    province = forms.CharField(max_length=100, required=False)
    postal_code = forms.CharField(max_length=20, required=False, label="Postal code")

    billing_same_as_shipping = forms.BooleanField(
        required=False,
        initial=True,
        label="Billing address same as shipping address",
    )
    billing_name = forms.CharField(max_length=120, required=False, label="Billing full name")
    billing_phone = forms.CharField(max_length=20, required=False, label="Billing phone")
    billing_street = forms.CharField(max_length=255, required=False, label="Billing street address")
    billing_city = forms.CharField(max_length=100, required=False, label="Billing city")
    billing_province = forms.CharField(max_length=100, required=False, label="Billing province")
    billing_postal_code = forms.CharField(max_length=20, required=False, label="Billing postal code")

    payment_method = forms.ChoiceField(
        choices=[
            ("cod", "Cash on Delivery"),
            ("esewa", "eSewa"),
            ("khalti", "Khalti"),
        ],
        widget=forms.RadioSelect,
        initial="cod",
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3}),
        required=False,
        label="Order notes (optional)",
    )
    save_address = forms.BooleanField(
        required=False,
        label="Save this address for future orders",
    )
    set_as_default = forms.BooleanField(
        required=False,
        label="Set as my default address",
    )
    address_label = forms.CharField(
        max_length=50,
        required=False,
        label="Address label (optional)",
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        input_class = {"class": "shop-input"}
        for name in (
            "full_name", "phone", "email", "street", "city",
            "province", "postal_code", "notes", "address_label",
            "billing_name", "billing_phone", "billing_street", "billing_city",
            "billing_province", "billing_postal_code",
        ):
            if name in self.fields:
                self.fields[name].widget.attrs.update(input_class)
        self.fields["shipping_area"].widget.attrs.update(input_class)
        self.fields["address_id"].widget.attrs.update(input_class)
        self.fields["address_label"].widget.attrs.setdefault(
            "placeholder", "e.g. Home, Office"
        )
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
            cleaned["save_address"] = False
            cleaned["set_as_default"] = False

        billing_same = cleaned.get("billing_same_as_shipping")
        if not billing_same:
            for field in ("billing_name", "billing_phone", "billing_street", "billing_city"):
                val = cleaned.get(field)
                if not val or not val.strip():
                    self.add_error(field, "This field is required when billing address differs.")
        else:
            cleaned["billing_name"] = cleaned.get("full_name")
            cleaned["billing_phone"] = cleaned.get("phone")
            cleaned["billing_street"] = cleaned.get("street")
            cleaned["billing_city"] = cleaned.get("city")
            cleaned["billing_province"] = cleaned.get("province", "")
            cleaned["billing_postal_code"] = cleaned.get("postal_code", "")

        return cleaned
