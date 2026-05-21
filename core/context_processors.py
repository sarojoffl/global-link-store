from products.models import Brand, Category


def store_defaults(request):
    """Shared template context for layout (nav, categories, cart placeholders)."""
    categories = list(Category.objects.order_by("name"))

    nav_items = []
    for category in categories:
        brands = (
            Brand.objects.filter(
                is_active=True,
                product__category=category,
            )
            .distinct()
            .order_by("order", "name")
        )
        nav_items.append({"category": category, "brands": brands})

    return {
        "categories": categories,
        "nav_items": nav_items,
        "cart_count": 0,
        "cart_total": "0.00",
        "wishlist_count": 0,
    }
