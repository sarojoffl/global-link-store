from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST

from products.models import Product

from .cart import (
    SHIPPING_COST,
    SHIPPING_FREE_THRESHOLD,
    add_to_cart,
    clear_cart,
    get_cart,
    get_cart_summary,
    remove_cart_item,
    update_cart_item,
)
from .forms import CheckoutForm
from .models import Order, OrderItem, WishlistItem


def cart_detail(request):
    cart = get_cart(request)
    summary = get_cart_summary(cart)
    return render(
        request,
        "shop/cart.html",
        {
            "cart": cart,
            **summary,
        },
    )


@require_POST
def cart_add(request):
    product_id = request.POST.get("product_id")
    quantity = request.POST.get("quantity", 1)
    variant_note = request.POST.get("variant_note", "")

    if not product_id:
        messages.error(request, "Invalid product.")
        return redirect(request.META.get("HTTP_REFERER", "shop:cart"))

    item, error = add_to_cart(request, product_id, quantity, variant_note)
    if error:
        messages.error(request, error)
    else:
        messages.success(
            request,
            f"{item.product.title} added to your cart.",
        )

    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER")
    if next_url and next_url.startswith("/"):
        return redirect(next_url)
    return redirect("shop:cart")


@require_POST
def cart_add_ajax(request):
    product_id = request.POST.get("product_id")
    quantity = request.POST.get("quantity", 1)
    variant_note = request.POST.get("variant_note", "")

    item, error = add_to_cart(request, product_id, quantity, variant_note)
    if error:
        return JsonResponse({"ok": False, "error": error}, status=400)

    cart = get_cart(request)
    summary = get_cart_summary(cart)
    return JsonResponse({
        "ok": True,
        "message": f"{item.product.title} added to cart.",
        "cart_count": summary["item_count"],
        "cart_total": str(summary["total"]),
    })


@require_POST
def cart_update(request, item_id):
    quantity = request.POST.get("quantity", 1)
    item, error = update_cart_item(request, item_id, quantity)
    if error:
        messages.error(request, error)
    elif item is None:
        messages.info(request, "Item removed from cart.")
    return redirect("shop:cart")


@require_POST
def cart_remove(request, item_id):
    remove_cart_item(request, item_id)
    messages.info(request, "Item removed from cart.")
    return redirect("shop:cart")


@login_required
def checkout(request):
    cart = get_cart(request)
    summary = get_cart_summary(cart)

    if not summary["items"]:
        messages.warning(request, "Your cart is empty.")
        return redirect("shop:cart")

    for item in summary["items"]:
        if not item.product.stock:
            messages.error(
                request,
                f"{item.product.title} is out of stock. Remove it to continue.",
            )
            return redirect("shop:cart")

    form = CheckoutForm(request.user, request.POST or None)

    if request.method == "POST" and form.is_valid():
        return _place_order(request, cart, summary, form)

    return render(
        request,
        "shop/checkout.html",
        {
            "form": form,
            "cart": cart,
            **summary,
            "shipping_free_threshold": SHIPPING_FREE_THRESHOLD,
        },
    )


def _place_order(request, cart, summary, form):
    data = form.cleaned_data

    with transaction.atomic():
        order = Order.objects.create(
            user=request.user,
            email=data["email"],
            shipping_name=data["full_name"],
            shipping_phone=data["phone"],
            shipping_street=data["street"],
            shipping_city=data["city"],
            shipping_province=data.get("province", ""),
            shipping_postal_code=data.get("postal_code", ""),
            payment_method=data["payment_method"],
            subtotal=summary["subtotal"],
            shipping_cost=summary["shipping"],
            total=summary["total"],
            notes=data.get("notes", ""),
        )

        for item in summary["items"]:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_title=item.product.title,
                variant_note=item.variant_note,
                quantity=item.quantity,
                unit_price=item.unit_price,
                line_total=item.line_total,
            )

        clear_cart(cart)

    messages.success(
        request,
        f"Order {order.order_number} placed successfully! We'll contact you soon.",
    )
    return redirect("shop:order_detail", order_number=order.order_number)


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).prefetch_related("items")
    return render(request, "shop/order_list.html", {"orders": orders})


@login_required
def order_detail(request, order_number):
    order = get_object_or_404(
        Order.objects.prefetch_related("items"),
        order_number=order_number,
        user=request.user,
    )
    return render(request, "shop/order_detail.html", {"order": order})


@login_required
def wishlist_view(request):
    items = (
        WishlistItem.objects.filter(user=request.user)
        .select_related("product", "product__category", "product__brand")
    )
    return render(request, "shop/wishlist.html", {"wishlist_items": items})


@login_required
@require_POST
def wishlist_toggle(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    item, created = WishlistItem.objects.get_or_create(
        user=request.user,
        product=product,
    )
    if not created:
        item.delete()
        added = False
        message = f"{product.title} removed from wishlist."
    else:
        added = True
        message = f"{product.title} added to wishlist."

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        from shop.context import get_wishlist_count

        return JsonResponse({
            "ok": True,
            "added": added,
            "message": message,
            "wishlist_count": get_wishlist_count(request),
        })

    messages.success(request, message)
    return redirect(request.META.get("HTTP_REFERER", "shop:wishlist"))
