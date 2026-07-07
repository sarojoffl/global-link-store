from products.models import Brand, Category
from shop.context import shop_context

WHATSAPP_NUMBER = "9779851402916"
WHATSAPP_DISPLAY_NUMBER = "+977-9851402916"


def store_defaults(request):
    """Shared template context for layout (nav, categories, cart, wishlist)."""
    categories = list(Category.objects.order_by("name"))

    nav_categories = Category.objects.filter(parent__isnull=True).prefetch_related(
        'children__children'
    ).order_by('id')

    ctx = shop_context(request)

    return {
        "categories": categories,
        "nav_categories": nav_categories,
        "whatsapp_number": WHATSAPP_NUMBER,
        "whatsapp_display_number": WHATSAPP_DISPLAY_NUMBER,
        **ctx,
    }