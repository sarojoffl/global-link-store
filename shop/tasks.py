from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from .models import Order


@shared_task
def send_order_confirmation_email(order_id):
    try:
        order = Order.objects.prefetch_related("items__product").get(pk=order_id)
    except Order.DoesNotExist:
        return

    mail_subject = f"Order Confirmed – {order.order_number}"
    message = render_to_string("shop/emails/order_confirmation.html", {
        "order": order,
    })
    email = EmailMessage(mail_subject, message, to=[order.email])
    email.content_subtype = "html"
    email.send()