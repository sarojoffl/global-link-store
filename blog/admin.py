from django.contrib import admin
from .models import BlogCategory, BlogPost


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "author", "is_published", "view_count", "created_at")
    list_filter = ("category", "is_published", "created_at")
    search_fields = ("title", "content", "excerpt")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("featured_products",)
    autocomplete_fields = ("featured_products",)
    fieldsets = (
        ("Article Information", {
            "fields": ("title", "slug", "category", "author", "featured_image", "excerpt", "content")
        }),
        ("Interactive Product Recommendations", {
            "fields": ("featured_products",)
        }),
        ("SEO Settings (Google SERP)", {
            "fields": ("meta_title", "meta_description", "faq_data")
        }),
        ("Publishing", {
            "fields": ("is_published",)
        }),
    )
