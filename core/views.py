from django.db.models import Q
from django.shortcuts import render
from .models import AboutSection, HeroSlide, HomePageSettings
from products.models import Product, Category, Brand


def _active_hero_slides(placement):
    return HeroSlide.objects.filter(
        active=True,
        placement=placement,
    ).filter(
        Q(media_type="image", image__isnull=False)
        | Q(media_type="video", video__isnull=False)
    ).order_by("order", "id")


def index(request):
    context = {
        "query": request.GET.get("q", ""),

        "home_settings": HomePageSettings.load(),
        "about_section": AboutSection.load(),
        "hero_slides_left": _active_hero_slides("left"),
        "hero_slides_right": _active_hero_slides("right"),

        "popular_categories": Category.objects.filter(
            is_popular=True
        )[:7],

        # Latest by created date
        "latest_products": Product.objects.order_by(
            "-created_at"
        )[:8],

        # Product type sections
        "featured_products": Product.objects.filter(
            product_type="featured"
        )[:8],

        "best_offers": Product.objects.filter(
            product_type="offer"
        )[:8],

        "new_arrivals": Product.objects.filter(
            product_type="new"
        )[:8],

        "brands": Brand.objects.filter(
            is_active=True
        ).order_by("order"),
    }

    return render(request, "core/index.html", context)