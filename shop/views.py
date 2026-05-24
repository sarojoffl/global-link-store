import base64
import json
import uuid

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

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
from .payments import generate_esewa_signature


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


def _create_order(request, summary, data):
    return Order.objects.create(
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


def _create_order_items(order, items):
    for item in items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            product_title=item.product.title,
            variant_note=item.variant_note,
            quantity=item.quantity,
            unit_price=item.unit_price,
            line_total=item.line_total,
        )


def _finalize_paid_order(request, order):
    cart = get_cart(request)
    clear_cart(cart)
    order.status = Order.STATUS_CONFIRMED
    order.save(update_fields=["status", "updated_at"])


def _initiate_khalti_payment(request, order, data):
    headers = {
        "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "return_url": settings.KHALTI_RETURN_URL,
        "website_url": settings.SITE_URL,
        "amount": int(order.total * 100),
        "purchase_order_id": order.order_number,
        "purchase_order_name": f"Order {order.order_number}",
        "customer_info": {
            "name": data["full_name"],
            "email": data["email"],
            "phone": data["phone"],
        },
    }

    response = requests.post(
        settings.KHALTI_INITIATE_URL,
        json=payload,
        headers=headers,
        timeout=30,
    )
    if response.status_code != 200:
        order.status = Order.STATUS_PAYMENT_FAILED
        order.save(update_fields=["status", "updated_at"])
        messages.error(request, "Could not start Khalti payment. Please try again.")
        return redirect("shop:order_detail", order_number=order.order_number)

    payment_data = response.json()
    payment_url = payment_data.get("payment_url")
    if not payment_url:
        order.status = Order.STATUS_PAYMENT_FAILED
        order.save(update_fields=["status", "updated_at"])
        messages.error(request, "Invalid response from Khalti.")
        return redirect("shop:order_detail", order_number=order.order_number)

    order.payment_id = payment_data.get("pidx", "")
    order.save(update_fields=["payment_id", "updated_at"])
    return redirect(payment_url)


def _initiate_esewa_payment(request, order):
    transaction_uuid = str(uuid.uuid4())
    base_url = settings.ESEWA_RETURN_URL.rstrip("/")
    esewa_data = {
        "amount": str(order.total),
        "tax_amount": "0",
        "total_amount": str(order.total),
        "transaction_uuid": transaction_uuid,
        "product_code": settings.ESEWA_PRODUCT_CODE,
        "product_service_charge": "0",
        "product_delivery_charge": "0",
        "success_url": f"{base_url}/{order.pk}/q/su/",
        "failure_url": f"{base_url}/{order.pk}/q/fu/",
        "signed_field_names": "total_amount,transaction_uuid,product_code",
    }

    signed_fields = esewa_data["signed_field_names"].split(",")
    esewa_data["signature"] = generate_esewa_signature(
        settings.ESEWA_SECRET_KEY,
        esewa_data,
        signed_fields,
    )
    order.payment_id = transaction_uuid
    order.save(update_fields=["payment_id", "updated_at"])

    return render(
        request,
        "payment/esewa_redirect.html",
        {
            "esewa_data": esewa_data,
            "esewa_payment_url": settings.ESEWA_PAYMENT_URL,
        },
    )


def _place_order(request, cart, summary, form):
    data = form.cleaned_data
    payment_method = data["payment_method"]

    with transaction.atomic():
        order = _create_order(request, summary, data)
        _create_order_items(order, summary["items"])

    if payment_method == Order.PAYMENT_KHALTI:
        return _initiate_khalti_payment(request, order, data)

    if payment_method == Order.PAYMENT_ESEWA:
        return _initiate_esewa_payment(request, order)

    with transaction.atomic():
        clear_cart(cart)

    messages.success(
        request,
        f"Order {order.order_number} placed successfully! We'll contact you soon.",
    )
    return redirect("shop:order_detail", order_number=order.order_number)


@csrf_exempt
def esewa_verify(request, order_id, status):
    order = get_object_or_404(Order, pk=order_id)
    ref_id = request.GET.get("refId")

    if not ref_id and "data" in request.GET:
        try:
            decoded_data = base64.b64decode(request.GET["data"]).decode("utf-8")
            data_json = json.loads(decoded_data)
            ref_id = data_json.get("transaction_uuid")
            status = "su" if data_json.get("status") == "COMPLETE" else "fu"
        except (json.JSONDecodeError, UnicodeDecodeError, KeyError):
            order.status = Order.STATUS_PAYMENT_FAILED
            order.save(update_fields=["status", "updated_at"])
            messages.error(request, "Payment verification failed.")
            return redirect("shop:order_detail", order_number=order.order_number)

    if status == "su" and ref_id:
        order.payment_id = ref_id
        _finalize_paid_order(request, order)
        messages.success(
            request,
            f"Payment received for order {order.order_number}. Thank you!",
        )
        return redirect("shop:order_detail", order_number=order.order_number)

    order.status = Order.STATUS_PAYMENT_FAILED
    order.save(update_fields=["status", "updated_at"])
    messages.error(request, "eSewa payment was not completed.")
    return redirect("shop:order_detail", order_number=order.order_number)


@csrf_exempt
def khalti_verify(request):
    pidx = request.GET.get("pidx")
    if not pidx:
        return HttpResponse("Missing pidx", status=400)

    order = Order.objects.filter(payment_id=pidx).first()
    if not order:
        return HttpResponse(f"Order with payment ID {pidx} not found", status=400)

    headers = {
        "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    response = requests.post(
        settings.KHALTI_LOOKUP_URL,
        json={"pidx": pidx},
        headers=headers,
        timeout=30,
    )

    if response.status_code != 200:
        order.status = Order.STATUS_PAYMENT_FAILED
        order.save(update_fields=["status", "updated_at"])
        messages.error(request, "Could not verify Khalti payment.")
        return redirect("shop:order_detail", order_number=order.order_number)

    payment_status = response.json().get("status")
    if payment_status == "Completed":
        _finalize_paid_order(request, order)
        messages.success(
            request,
            f"Payment received for order {order.order_number}. Thank you!",
        )
        return redirect("shop:order_detail", order_number=order.order_number)

    order.status = Order.STATUS_PAYMENT_FAILED
    order.save(update_fields=["status", "updated_at"])
    messages.error(request, "Khalti payment was not completed.")
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
