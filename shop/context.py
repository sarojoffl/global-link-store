from decimal import Decimal

from .cart import get_cart, get_cart_summary
from .models import WishlistItem


def get_wishlist_count(request):
    if request.user.is_authenticated:
        return WishlistItem.objects.filter(user=request.user).count()
    return 0


def shop_context(request):
    cart = get_cart(request)
    summary = get_cart_summary(cart)
    return {
        "cart_count": summary["item_count"],
        "cart_total": f"{summary['total']:.2f}",
        "wishlist_count": get_wishlist_count(request),
    }
