from celery import shared_task
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.models import User
from .tokens import account_activation_token


@shared_task
def send_verification_email(user_id, domain):
    user = User.objects.get(id=user_id)

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)

    mail_subject = "Verify Your Email Address"

    message = render_to_string("accounts/verify_email.html", {
        "user": user,
        "domain": domain,
        "uid": uid,
        "token": token,
    })

    email = EmailMessage(mail_subject, message, to=[user.email])
    email.send()