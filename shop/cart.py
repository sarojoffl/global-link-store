from decimal import Decimal

from django.db import transaction

from products.models import Product, ProductSKU

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
        for item in session_cart.items.select_related("product", "sku"):
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


def normalize_combo(combo: str) -> str:
    """Match frontend: sort comma-separated key:value pairs case-insensitively."""
    parts = [p.strip().lower() for p in (combo or "").split(",") if p.strip()]
    return ",".join(sorted(parts))


def resolve_sku(product, variant_combo):
    normalized = normalize_combo(variant_combo or "")

    for sku in ProductSKU.objects.filter(product=product):
        if normalize_combo(sku.variant_combo) == normalized:
            return sku

    return None


def calculate_unit_price(product, sku):
    """Price is base product price + SKU adjustment."""
    return product.price + sku.price_adjustment


def add_to_cart(request, product_id, quantity=1, variant_note=""):
    product = Product.objects.filter(pk=product_id).first()
    if not product:
        return None, "Product not found."

    variant_combo = (variant_note or "").strip()[:255]

    sku = resolve_sku(product, variant_combo)

    # If no SKU found and no variants exist, try the default blank SKU
    if not sku and not product.productvariantgroup_set.exists():
        sku = ProductSKU.objects.filter(
            product=product,
            variant_combo="",
        ).first()

    if not sku:
        return None, "Invalid variant selected."

    if not sku.is_in_stock:
        return None, "This variant is out of stock."

    max_qty = min(sku.stock, 10)
    quantity = max(1, min(int(quantity), max_qty))
    unit_price = calculate_unit_price(product, sku)

    cart = get_cart(request)
    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        variant_note=variant_combo,
        defaults={
            "quantity": quantity,
            "unit_price": unit_price,
            "sku": sku,
        },
    )
    if not created:
        new_qty = min(item.quantity + quantity, max_qty)
        item.quantity = new_qty
        item.unit_price = unit_price
        item.sku = sku
        item.save(update_fields=["quantity", "unit_price", "sku"])

    return item, None


def update_cart_item(request, item_id, quantity):
    cart = get_cart(request)
    item = cart.items.filter(pk=item_id).select_related("product", "sku").first()
    if not item:
        return None, "Item not found."

    quantity = int(quantity)
    if quantity < 1:
        item.delete()
        return None, None

    if item.sku:
        max_qty = min(item.sku.stock, 10)
        if quantity > item.sku.stock:
            return None, f"Only {item.sku.stock} units available."
        quantity = min(quantity, max_qty)

    item.quantity = quantity
    item.save(update_fields=["quantity"])
    return item, None


def remove_cart_item(request, item_id):
    cart = get_cart(request)
    cart.items.filter(pk=item_id).delete()


def get_cart_summary(cart):
    items = list(
        cart.items.select_related(
            "product", "product__brand", "product__category", "sku"
        )
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