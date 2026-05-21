from django.contrib import admin
from .models import AboutSection, HeroSlide, HomePageSettings


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ("id", "placement", "media_type", "active", "order", "url")
    list_editable = ("placement", "media_type", "active", "order")
    list_filter = ("placement", "media_type", "active")
    ordering = ("placement", "order", "id")
    fieldsets = (
        (None, {"fields": ("placement", "media_type", "active", "order", "url")}),
        (
            "Media",
            {
                "fields": ("image", "video"),
                "description": "Upload an image OR a video file depending on media type.",
            },
        ),
    )


@admin.register(HomePageSettings)
class HomePageSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Top zone background",
            {
                "fields": ("top_zone_background",),
                "description": "Shown behind the dual hero sliders and brand logos until Popular Categories.",
            },
        ),
    )

    def has_add_permission(self, request):
        return not HomePageSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AboutSection)
class AboutSectionAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Content",
            {"fields": ("is_active", "title", "heading", "description")},
        ),
        (
            "Stats (animated counters on homepage)",
            {
                "fields": (
                    "products_listed",
                    "orders_delivered",
                    "happy_customers",
                    "years_of_service",
                ),
            },
        ),
    )

    def has_add_permission(self, request):
        return not AboutSection.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
