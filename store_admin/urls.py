from django.urls import path
from . import views

app_name = "store_admin"

urlpatterns = [
    path("", views.dashboard_home, name="dashboard_home"),

    # Hero Slides
    path("hero-slides/", views.heroslide_list, name="heroslide_list"),
    path("hero-slides/add/", views.heroslide_add, name="heroslide_add"),
    path("hero-slides/<int:pk>/edit/", views.heroslide_edit, name="heroslide_edit"),
    path("hero-slides/<int:pk>/delete/", views.heroslide_delete, name="heroslide_delete"),

    # Homepage Settings
    path("homepage-settings/", views.homepage_settings, name="homepage_settings"),

    # About Section
    path("about-section/", views.about_section, name="about_section"),

    # Categories
    path("categories/", views.category_list, name="category_list"),
    path("categories/add/", views.category_add, name="category_add"),
    path("categories/<int:pk>/edit/", views.category_edit, name="category_edit"),
    path("categories/<int:pk>/delete/", views.category_delete, name="category_delete"),

    # Brands
    path("brands/", views.brand_list, name="brand_list"),
    path("brands/add/", views.brand_add, name="brand_add"),
    path("brands/<int:pk>/edit/", views.brand_edit, name="brand_edit"),
    path("brands/<int:pk>/delete/", views.brand_delete, name="brand_delete"),

    # Products
    path("products/", views.product_list, name="product_list"),
    path("products/add/", views.product_add, name="product_add"),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
    path("products/<int:pk>/edit/", views.product_edit, name="product_edit"),
    path("products/<int:pk>/delete/", views.product_delete, name="product_delete"),

    # Inventory (all SKUs)
    path("inventory/", views.inventory_list, name="inventory_list"),

    # Product Variant Groups and Options
    path("products/<int:product_pk>/variant-groups/add/", views.variant_group_add, name="variant_group_add"),
    path("variant-groups/<int:pk>/edit/", views.variant_group_edit, name="variant_group_edit"),
    path("variant-groups/<int:pk>/delete/", views.variant_group_delete, name="variant_group_delete"),
    path("variant-groups/<int:group_pk>/options/add/", views.variant_option_add, name="variant_option_add"),
    path("variant-options/<int:pk>/edit/", views.variant_option_edit, name="variant_option_edit"),
    path("variant-options/<int:pk>/delete/", views.variant_option_delete, name="variant_option_delete"),

    # Product SKUs
    path("products/<int:product_pk>/skus/add/", views.sku_add, name="sku_add"),
    path("skus/<int:pk>/edit/", views.sku_edit, name="sku_edit"),
    path("skus/<int:pk>/delete/", views.sku_delete, name="sku_delete"),

    # Product Images
    path("products/<int:product_pk>/images/add/", views.product_image_add, name="product_image_add"),
    path("product-images/<int:pk>/delete/", views.product_image_delete, name="product_image_delete"),

    # Product Specifications
    path("products/<int:product_pk>/specs/add/", views.product_spec_add, name="product_spec_add"),
    path("product-specs/<int:pk>/edit/", views.product_spec_edit, name="product_spec_edit"),
    path("product-specs/<int:pk>/delete/", views.product_spec_delete, name="product_spec_delete"),

    # Product Reviews
    path("product-reviews/", views.product_review_list, name="product_review_list"),
    path("product-reviews/<int:pk>/", views.product_review_detail, name="product_review_detail"),
    path("product-reviews/<int:pk>/edit/", views.product_review_edit, name="product_review_edit"),
    path("product-reviews/<int:pk>/toggle-publish/", views.product_review_toggle_publish, name="product_review_toggle_publish"),
    path("product-reviews/<int:pk>/delete/", views.product_review_delete, name="product_review_delete"),

    # Orders
    path("orders/", views.order_list, name="order_list"),
    path("orders/<int:pk>/", views.order_detail, name="order_detail"),

    # Customers
    path("customers/", views.customer_list, name="customer_list"),
    path("customers/<int:pk>/", views.customer_detail, name="customer_detail"),
    path("customers/<int:pk>/edit/", views.customer_edit, name="customer_edit"),
    path("customers/<int:user_pk>/addresses/add/", views.customer_address_add, name="customer_address_add"),
    path("customer-addresses/<int:pk>/edit/", views.customer_address_edit, name="customer_address_edit"),
    path("customer-addresses/<int:pk>/delete/", views.customer_address_delete, name="customer_address_delete"),

    # ── Support (Contact + Newsletter) ──
    path("contact-messages/", views.contact_message_list, name="contact_message_list"),
    path("contact-messages/<int:pk>/", views.contact_message_detail, name="contact_message_detail"),
    path("contact-messages/<int:pk>/mark-read/", views.contact_message_mark_read, name="contact_message_mark_read"),
    path("contact-messages/<int:pk>/delete/", views.contact_message_delete, name="contact_message_delete"),

    path("newsletter-subscribers/", views.newsletter_subscriber_list, name="newsletter_subscriber_list"),
    path("newsletter-subscribers/<int:pk>/toggle-active/", views.newsletter_subscriber_toggle_active, name="newsletter_subscriber_toggle_active"),
    path("newsletter-subscribers/<int:pk>/delete/", views.newsletter_subscriber_delete, name="newsletter_subscriber_delete"),
]
