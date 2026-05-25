from django.urls import path

from . import views

app_name = "shop"

urlpatterns = [
    path("cart/", views.cart_detail, name="cart"),
    path("cart/add/", views.cart_add, name="cart_add"),
    path("cart/add/ajax/", views.cart_add_ajax, name="cart_add_ajax"),
    path("cart/update/<int:item_id>/", views.cart_update, name="cart_update"),
    path("cart/remove/<int:item_id>/", views.cart_remove, name="cart_remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("payment/esewa/<int:order_id>/q/<str:status>/", views.esewa_verify, name="esewa_verify"),
    path("payment/khalti/verify/", views.khalti_verify, name="khalti_verify"),
    path("orders/", views.order_list, name="order_list"),
    path("orders/<str:order_number>/", views.order_detail, name="order_detail"),
    path("orders/<str:order_number>/invoice/", views.order_invoice, name="order_invoice"),
    path("wishlist/", views.wishlist_view, name="wishlist"),
    path("wishlist/toggle/<int:product_id>/", views.wishlist_toggle, name="wishlist_toggle"),
]
