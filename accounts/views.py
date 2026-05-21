from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm
from .tasks import send_verification_email, send_password_reset_email
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.models import User
from .tokens import account_activation_token
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import SetPasswordForm
from django.utils.http import urlsafe_base64_decode


def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:index')

    form = RegisterForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            domain = get_current_site(request).domain
            send_verification_email.delay(user.id, domain)
            return render(request, 'accounts/check_email.html')

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:index')

    form = LoginForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Remember me
            if request.POST.get('remember'):
                request.session.set_expiry(60 * 60 * 24 * 30)  # 30 days
            else:
                request.session.set_expiry(0)  # expires when browser closes

            messages.success(request, f"Welcome back, {user.username}!")
            return redirect(request.GET.get('next', 'core:index'))
        else:
            messages.error(request, "Login failed. Check credentials or verify email.")

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('accounts:login')


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Email verification completed successfully.")
        return redirect('accounts:login')
    else:
        messages.error(request, "The activation link is invalid or has expired.")
        return redirect('accounts:register')


# ───────── PASSWORD RESET ─────────

def password_reset_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        domain = get_current_site(request).domain
        if email:
            send_password_reset_email.delay(email, domain)
        # always redirect — never reveal if email exists
        return redirect('accounts:password_reset_done')

    return render(request, 'accounts/password_reset.html')


def password_reset_done_view(request):
    return render(request, 'accounts/password_reset_done.html')


def password_reset_confirm_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    valid = user is not None and default_token_generator.check_token(user, token)

    if request.method == 'POST' and valid:
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            return redirect('accounts:password_reset_complete')
    else:
        form = SetPasswordForm(user) if valid else None

    return render(request, 'accounts/password_reset_confirm.html', {
        'form': form,
        'validlink': valid,
    })


def password_reset_complete_view(request):
    return render(request, 'accounts/password_reset_complete.html')