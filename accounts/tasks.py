from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from .tokens import account_activation_token


@shared_task
def send_verification_email(user_id, domain):
    user = User.objects.get(id=user_id)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)
    mail_subject = "Verify Your Email Address"
    message = render_to_string("accounts/emails/verify_email.html", {
        "user": user,
        "domain": domain,
        "uid": uid,
        "token": token,
    })
    email = EmailMessage(mail_subject, message, to=[user.email])
    email.send()


@shared_task
def send_password_reset_email(email, domain):
    try:
        user = User.objects.get(email=email, is_active=True)
    except User.DoesNotExist:
        return  # silently do nothing

    uid   = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    link  = f"http://{domain}/accounts/password-reset/confirm/{uid}/{token}/"

    message = render_to_string("accounts/emails/password_reset_email.html", {
        "user": user,
        "link": link,
    })

    email_msg = EmailMessage(
        subject="Reset your Global Link Store password",
        body=message,
        to=[email],
    )
    email_msg.send()