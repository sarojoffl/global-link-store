def activate_user(backend, user, response, *args, **kwargs):
    if not user.is_active:
        user.is_active = True
        user.save()


def setup_user_account(backend, user, response, *args, **kwargs):
    from accounts.models import UserProfile

    UserProfile.objects.get_or_create(user=user)


def merge_cart_on_login(backend, user, response, request=None, *args, **kwargs):
    if request is None:
        return
    from shop.cart import merge_session_cart_into_user

    merge_session_cart_into_user(request, user)
