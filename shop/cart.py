from decimal import Decimal

from django.db import transaction

from products.models import Product, ProductVariantOption

from .models import Cart, CartItem

SHIPPING_FREE_THRESHOLD = Decimal("5000")
SHIPPING_COST = Decimal("150")


def ensure_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def get_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(
            user=request.user,
            defaults={"session_key": ""},
        )
        return cart

    session_key = ensure_session_key(request)
    cart, _ = Cart.objects.get_or_create(user=None, session_key=session_key)
    return cart


def merge_session_cart_into_user(request, user):
    session_key = request.session.session_key
    if not session_key:
        return

    session_cart = Cart.objects.filter(user=None, session_key=session_key).first()
    if not session_cart or not session_cart.items.exists():
        return

    user_cart, _ = Cart.objects.get_or_create(user=user, defaults={"session_key": ""})

    with transaction.atomic():
        for item in session_cart.items.select_related("product"):
            existing = user_cart.items.filter(
                product=item.product,
                variant_note=item.variant_note,
            ).first()
            if existing:
                existing.quantity += item.quantity
                existing.save(update_fields=["quantity"])
            else:
                item.cart = user_cart
                item.save(update_fields=["cart"])
        session_cart.delete()


def calculate_unit_price(product, variant_note=""):
    price = product.price
    if not variant_note:
        return price

    adjustments = Decimal("0")
    for part in variant_note.split(","):
        part = part.strip()
        if ":" in part:
            value = part.split(":", 1)[1].strip()
            option = ProductVariantOption.objects.filter(
                group__product=product,
                value=value,
            ).first()
            if option:
                adjustments += option.price_adjustment
    return price + adjustments


def add_to_cart(request, product_id, quantity=1, variant_note=""):
    product = Product.objects.filter(pk=product_id, stock=True).first()
    if not product:
        return None, "Product is unavailable."

    quantity = max(1, min(int(quantity), 10))
    variant_note = (variant_note or "").strip()[:255]
    unit_price = calculate_unit_price(product, variant_note)

    cart = get_cart(request)
    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        variant_note=variant_note,
        defaults={"quantity": quantity, "unit_price": unit_price},
    )
    if not created:
        item.quantity = min(item.quantity + quantity, 10)
        item.unit_price = unit_price
        item.save(update_fields=["quantity", "unit_price"])

    return item, None


def update_cart_item(request, item_id, quantity):
    cart = get_cart(request)
    item = cart.items.filter(pk=item_id).select_related("product").first()
    if not item:
        return None, "Item not found."

    quantity = int(quantity)
    if quantity < 1:
        item.delete()
        return None, None

    item.quantity = min(quantity, 10)
    item.save(update_fields=["quantity"])
    return item, None


def remove_cart_item(request, item_id):
    cart = get_cart(request)
    cart.items.filter(pk=item_id).delete()


def get_cart_summary(cart):
    items = list(
        cart.items.select_related("product", "product__brand", "product__category")
    )
    subtotal = sum((i.line_total for i in items), Decimal("0"))
    item_count = sum(i.quantity for i in items)
    shipping = Decimal("0") if subtotal >= SHIPPING_FREE_THRESHOLD or not items else SHIPPING_COST
    total = subtotal + shipping
    return {
        "items": items,
        "subtotal": subtotal,
        "shipping": shipping,
        "total": total,
        "item_count": item_count,
    }


def clear_cart(cart):
    cart.items.all().delete()
