from products.models import Brand, Category
from shop.context import shop_context


def store_defaults(request):
    """Shared template context for layout (nav, categories, cart, wishlist)."""
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

    ctx = shop_context(request)

    return {
        "categories": categories,
        "nav_items": nav_items,
        **ctx,
    }
