from django import forms
from django.contrib.auth.models import User

from accounts.models import Address, UserProfile
from core.models import HeroBanner, HeroSlide, HomePageSettings, AboutSection
from products.models import (
    Category, Brand, Product, ProductImage, ProductReview, ProductSKU,
    ProductSpecification, ProductVariantGroup, ProductVariantOption,
)
from shop.models import Order


class BaseAdminForm(forms.ModelForm):
    """Apply Bootstrap classes to all fields."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault("class", "form-select")
            elif isinstance(field.widget, forms.RadioSelect):
                field.widget.attrs.setdefault("class", "form-check-input")
            else:
                field.widget.attrs.setdefault("class", "form-control")


class HeroSlideForm(BaseAdminForm):
    class Meta:
        model = HeroSlide
        fields = ["placement", "media_type", "image", "video", "url", "active", "order"]
        widgets = {
            "url": forms.TextInput(attrs={"placeholder": "/products/ or https://..."}),
            "order": forms.NumberInput(attrs={"min": 0}),
        }


class HeroBannerForm(BaseAdminForm):
    class Meta:
        model = HeroBanner
        fields = ["placement", "title", "subtitle", "cta_label", "link", "background", "image", "active", "order"]
        widgets = {
            "title":     forms.TextInput(attrs={"placeholder": "e.g. Best Deals"}),
            "subtitle":  forms.TextInput(attrs={"placeholder": "e.g. Up to 50% off"}),
            "cta_label": forms.TextInput(attrs={"placeholder": "e.g. Buy Now"}),
            "link":      forms.TextInput(attrs={"placeholder": "/products/ or https://..."}),
            "order":     forms.NumberInput(attrs={"min": 0}),
        }


class HomePageSettingsForm(BaseAdminForm):
    class Meta:
        model = HomePageSettings
        fields = ["top_zone_background"]


class AboutSectionForm(BaseAdminForm):
    class Meta:
        model = AboutSection
        fields = [
            "title", "heading", "description",
            "products_listed", "orders_delivered",
            "happy_customers", "years_of_service", "is_active",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class CategoryForm(BaseAdminForm):
    class Meta:
        model = Category
        fields = ["name", "parent", "image", "is_popular"]

        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "e.g. Laptops"}),
            "image": forms.ClearableFileInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add labels and customize queryset
        self.fields["parent"].required = False
        self.fields["parent"].empty_label = "None (Root Category)"

        if self.instance and self.instance.pk:
            from products.catalog import _get_descendants

            descendants = _get_descendants(self.instance)
            descendant_ids = [d.pk for d in descendants]

            self.fields["parent"].queryset = Category.objects.exclude(
                pk__in=descendant_ids
            )
        else:
            self.fields["parent"].queryset = Category.objects.all()


class BrandForm(BaseAdminForm):
    class Meta:
        model = Brand
        fields = ["name", "logo", "url", "is_active", "order"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "e.g. Apple"}),
            "url": forms.URLInput(attrs={"placeholder": "https://..."}),
            "order": forms.NumberInput(attrs={"min": 0}),
        }


class ProductForm(BaseAdminForm):
    class Meta:
        model = Product
        fields = [
            "title", "category", "brand", "price", "old_price",
            "image", "description", "product_type",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Product name"}),
            "price": forms.NumberInput(attrs={"min": 0, "step": "0.01"}),
            "old_price": forms.NumberInput(attrs={"min": 0, "step": "0.01"}),
            "description": forms.Textarea(attrs={"rows": 5}),
        }


class ProductSKUForm(BaseAdminForm):
    class Meta:
        model = ProductSKU
        fields = ["variant_combo", "stock", "price_adjustment"]
        widgets = {
            "variant_combo": forms.TextInput(attrs={
                "placeholder": 'Leave blank for default, or e.g. Color:Black,Variant:8GB+128GB',
            }),
            "stock": forms.NumberInput(attrs={"min": 0}),
            "price_adjustment": forms.NumberInput(attrs={"step": "0.01"}),
        }


class ProductVariantGroupForm(BaseAdminForm):
    class Meta:
        model = ProductVariantGroup
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "e.g. Color, Variant"}),
        }


class ProductVariantOptionForm(BaseAdminForm):
    class Meta:
        model = ProductVariantOption
        fields = ["value"]
        widgets = {
            "value": forms.TextInput(attrs={"placeholder": "e.g. Black, 8GB+128GB"}),
        }


class ProductImageForm(BaseAdminForm):
    class Meta:
        model = ProductImage
        fields = ["image", "order"]
        widgets = {
            "order": forms.NumberInput(attrs={"min": 0}),
        }


class ProductSpecificationForm(BaseAdminForm):
    class Meta:
        model = ProductSpecification
        fields = ["section", "name", "value", "is_key"]
        widgets = {
            "section": forms.TextInput(attrs={"placeholder": "e.g. General"}),
            "name": forms.TextInput(attrs={"placeholder": "e.g. Weight"}),
            "value": forms.TextInput(attrs={"placeholder": "e.g. 1.5 kg"}),
        }


class OrderStatusForm(BaseAdminForm):
    class Meta:
        model = Order
        fields = ["status", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class CustomerForm(BaseAdminForm):
    phone = forms.CharField(max_length=20, required=False, label="Phone")
    photo = forms.ImageField(required=False, label="Profile Photo", widget=forms.ClearableFileInput(attrs={"accept": "image/*"}))

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "is_active"]
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "First name"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Last name"}),
            "email": forms.EmailInput(attrs={"placeholder": "email@example.com"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            profile, _ = UserProfile.objects.get_or_create(user=self.instance)
            self.fields["phone"].initial = profile.phone
            self.fields["photo"].initial = profile.photo


class CustomerAddressForm(BaseAdminForm):
    class Meta:
        model = Address
        fields = [
            "label", "full_name", "phone", "street",
            "city", "province", "postal_code", "is_default",
        ]
        widgets = {
            "label": forms.TextInput(attrs={"placeholder": "e.g. Home"}),
            "street": forms.TextInput(attrs={"placeholder": "Street address"}),
            "city": forms.TextInput(attrs={"placeholder": "City"}),
            "province": forms.TextInput(attrs={"placeholder": "Province"}),
            "postal_code": forms.TextInput(attrs={"placeholder": "Postal code"}),
        }


class ProductReviewAdminForm(BaseAdminForm):
    class Meta:
        model = ProductReview
        fields = ["rating", "title", "body", "is_published"]
        widgets = {
            "rating": forms.NumberInput(attrs={"min": 1, "max": 5}),
            "title": forms.TextInput(attrs={"placeholder": "Review title"}),
            "body": forms.Textarea(attrs={"rows": 5}),
        }
