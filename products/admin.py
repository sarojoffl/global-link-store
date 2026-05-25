from django.contrib import admin

from .models import (
    Brand,
    Category,
    Product,
    ProductImage,
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


class ProductVariantGroupInline(admin.StackedInline):
    model = ProductVariantGroup
    extra = 0
    show_change_link = True


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "brand", "price", "stock", "product_type")
    list_filter = ("category", "brand", "stock", "product_type")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [
        ProductImageInline,
        ProductVariantGroupInline,
        ProductSpecificationInline,
    ]


@admin.register(ProductVariantGroup)
class ProductVariantGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "product")
    inlines = [ProductVariantOptionInline]


admin.site.register(Category)
admin.site.register(Brand)
