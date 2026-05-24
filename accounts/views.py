from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm, ProfileForm, AddressForm
from .models import Address, UserProfile
from .tasks import send_verification_email, send_password_reset_email
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.models import User
from .tokens import account_activation_token
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import SetPasswordForm
from shop.cart import merge_session_cart_into_user
from shop.models import Order, WishlistItem


def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:index')

    form = RegisterForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            UserProfile.objects.get_or_create(user=user)
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
            merge_session_cart_into_user(request, user)

            if request.POST.get('remember'):
                request.session.set_expiry(60 * 60 * 24 * 30)
            else:
                request.session.set_expiry(0)

            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
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
    except Exception:
        user = None

    if user and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        UserProfile.objects.get_or_create(user=user)
        messages.success(request, "Email verification completed successfully.")
        return redirect('accounts:login')
    else:
        messages.error(request, "The activation link is invalid or has expired.")
        return redirect('accounts:register')


@login_required
def dashboard(request):
    recent_orders = Order.objects.filter(user=request.user)[:5]
    order_count = Order.objects.filter(user=request.user).count()
    wishlist_count = WishlistItem.objects.filter(user=request.user).count()
    address_count = Address.objects.filter(user=request.user).count()

    return render(request, 'accounts/dashboard.html', {
        'recent_orders': recent_orders,
        'order_count': order_count,
        'wishlist_count': wishlist_count,
        'address_count': address_count,
    })


@login_required
def profile_view(request):
    form = ProfileForm(request.user, request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('accounts:profile')
        messages.error(request, "Please correct the errors below.")

    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def address_list(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'accounts/address_list.html', {'addresses': addresses})


@login_required
def address_add(request):
    form = AddressForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, "Address saved.")
            return redirect('accounts:addresses')
        messages.error(request, "Please correct the errors below.")

    return render(request, 'accounts/address_form.html', {
        'form': form,
        'title': 'Add Address',
    })


@login_required
def address_edit(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    form = AddressForm(request.POST or None, instance=address)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Address updated.")
            return redirect('accounts:addresses')
        messages.error(request, "Please correct the errors below.")

    return render(request, 'accounts/address_form.html', {
        'form': form,
        'title': 'Edit Address',
        'address': address,
    })


@login_required
def address_delete(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        address.delete()
        messages.info(request, "Address deleted.")
        return redirect('accounts:addresses')
    return render(request, 'accounts/address_confirm_delete.html', {'address': address})


def password_reset_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        domain = get_current_site(request).domain
        if email:
            send_password_reset_email.delay(email, domain)
        return redirect('accounts:password_reset_done')

    return render(request, 'accounts/password_reset.html')


def password_reset_done_view(request):
    return render(request, 'accounts/password_reset_done.html')


def password_reset_confirm_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
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
