from celery import shared_task
from django.core.mail import EmailMessage, send_mail
from django.template.loader import render_to_string
from django.conf import settings

from .models import Order


@shared_task
def send_order_confirmation_email(order_id):
    try:
        order = Order.objects.prefetch_related("items__product").get(pk=order_id)
    except Order.DoesNotExist:
        return

    message = render_to_string("shop/emails/order_confirmation.html", {"order": order})
    email = EmailMessage(
        subject=f"Order Confirmed – {order.order_number}",
        body=message,
        to=[order.email],
    )
    email.content_subtype = "html"
    email.send()


def _send_order_status_email(order_id, subject, template_name):
    try:
        order = Order.objects.prefetch_related("items").get(pk=order_id)
    except Order.DoesNotExist:
        return

    message = render_to_string(template_name, {"order": order})
    email = EmailMessage(subject=subject, body=message, to=[order.email])
    email.content_subtype = "html"
    email.send()


@shared_task
def send_order_shipped_email(order_id):
    order = Order.objects.filter(pk=order_id, status=Order.STATUS_SHIPPED).first()
    if not order:
        return
    _send_order_status_email(
        order_id,
        f"Your order has shipped – {order.order_number}",
        "shop/emails/order_shipped.html",
    )


@shared_task
def send_order_delivered_email(order_id):
    order = Order.objects.filter(pk=order_id, status=Order.STATUS_DELIVERED).first()
    if not order:
        return
    _send_order_status_email(
        order_id,
        f"Your order was delivered – {order.order_number}",
        "shop/emails/order_delivered.html",
    )


@shared_task
def send_admin_order_notification(order_id):
    try:
        order = Order.objects.prefetch_related("items").get(pk=order_id)
    except Order.DoesNotExist:
        return

    lines = [
        f"New order received: {order.order_number}",
        f"Customer: {order.shipping_name} ({order.email})",
        f"Phone: {order.shipping_phone}",
        f"Payment: {order.get_payment_method_display()}",
        f"Total: Rs {order.total}",
        "",
        "Items:",
    ]
    for item in order.items.all():
        lines.append(f"  - {item.product_title} x{item.quantity} = Rs {item.line_total}")
    lines += [
        "",
        f"Ship to: {order.shipping_street}, {order.shipping_city}",
    ]
    if order.notes:
        lines.append(f"Notes: {order.notes}")

    send_mail(
        subject=f"[New Order] {order.order_number} – Rs {order.total}",
        message="\n".join(lines),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.ADMIN_ORDER_EMAIL],
    )