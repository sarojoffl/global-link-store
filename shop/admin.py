from django.contrib import admin

from .models import Cart, CartItem, Order, OrderItem, WishlistItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "session_key", "updated_at")
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_title", "variant_note", "quantity", "unit_price", "line_total")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "user", "status", "total", "payment_method", "created_at")
    list_filter = ("status", "payment_method", "created_at")
    search_fields = ("order_number", "email", "shipping_name", "shipping_phone")
    readonly_fields = ("order_number", "created_at", "updated_at")
    inlines = [OrderItemInline]


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "created_at")
    list_filter = ("created_at",)
