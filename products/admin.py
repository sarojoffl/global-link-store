from django.contrib import admin
from .utils import format_variant_combo

from .models import (
    Brand,
    Category,
    Product,
    ProductImage,
    ProductSKU,
    ProductSpecification,
    ProductVariantGroup,
    ProductVariantOption,
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 2
    fields = ("section", "name", "value", "is_key")


class ProductVariantOptionInline(admin.TabularInline):
    model = ProductVariantOption
    extra = 1
    fields = ("value",)


class ProductVariantGroupInline(admin.StackedInline):
    model = ProductVariantGroup
    extra = 0
    show_change_link = True


class ProductSKUInline(admin.TabularInline):
    model = ProductSKU
    extra = 1
    fields = ("variant_combo", "stock", "price_adjustment")
    help_texts = {
        "variant_combo": 'e.g. "Color:Black,Variant:8GB+128GB" — leave blank for products with no variants'
    }


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "brand", "price", "is_in_stock", "product_type")
    list_filter = ("category", "brand", "product_type")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [
        ProductImageInline,
        ProductVariantGroupInline,
        ProductSKUInline,
        ProductSpecificationInline,
    ]

    def is_in_stock(self, obj):
        return obj.is_in_stock
    is_in_stock.boolean = True
    is_in_stock.short_description = "In Stock"


@admin.register(ProductVariantGroup)
class ProductVariantGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "product")
    inlines = [ProductVariantOptionInline]


@admin.register(ProductSKU)
class ProductSKUAdmin(admin.ModelAdmin):
    list_display = ("product", "combo_display", "stock", "price_adjustment", "is_in_stock")

    def combo_display(self, obj):
        return format_variant_combo(obj.variant_combo)

    combo_display.short_description = "Variant combo"


admin.site.register(Category)
admin.site.register(Brand)