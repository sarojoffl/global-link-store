from django.shortcuts import render
from .models import Brand, Product, Category, HeroSlide


def index(request):

    context = {
        "query": request.GET.get("q", ""),

        "hero_slides": HeroSlide.objects.filter(active=True),

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