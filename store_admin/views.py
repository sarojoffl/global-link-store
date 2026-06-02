from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse

from accounts.models import Address, UserProfile

from core.models import (
    AboutSection,
    ContactMessage,
    HeroBanner,
    HeroSlide,
    HomePageSettings,
    HomePageSettings,
    NewsletterSubscriber,
)
from products.models import (
    Category, Brand, Product, ProductImage, ProductReview, ProductSKU,
    ProductSpecification, ProductVariantGroup, ProductVariantOption,
)
from shop.models import Order
from shop.tasks import send_order_delivered_email, send_order_shipped_email
from .forms import (
    HeroBannerForm, HeroSlideForm, HomePageSettingsForm, AboutSectionForm,
    CategoryForm, BrandForm, ProductForm, ProductSKUForm,
    ProductImageForm, ProductSpecificationForm, OrderStatusForm,
    ProductVariantGroupForm, ProductVariantOptionForm,
    CustomerForm, CustomerAddressForm, ProductReviewAdminForm,
)

staff_required = user_passes_test(lambda u: u.is_active and u.is_staff)


@login_required
@staff_required
def dashboard_home(request):
    recent_orders = Order.objects.order_by("-created_at")[:5]
    pending_orders = Order.objects.filter(status=Order.STATUS_PENDING).count()
    total_orders = Order.objects.count()
    low_stock_skus = ProductSKU.objects.filter(stock__lte=5, stock__gt=0).select_related("product")[:10]
    out_of_stock_skus = ProductSKU.objects.filter(stock=0).select_related("product").count()

    return render(request, "store_admin/dashboard_home.html", {
        "recent_orders": recent_orders,
        "pending_orders": pending_orders,
        "total_orders": total_orders,
        "low_stock_skus": low_stock_skus,
        "out_of_stock_skus": out_of_stock_skus,
    })


# ── HERO SLIDES ──

@login_required
@staff_required
def heroslide_list(request):
    slides = HeroSlide.objects.all()
    return render(request, "store_admin/heroslide_list.html", {"slides": slides})


@login_required
@staff_required
def heroslide_add(request):
    form = HeroSlideForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Hero slide added successfully.")
        return redirect("store_admin:heroslide_list")
    return render(request, "store_admin/generic_form.html", {
        "form": form,
        "title": "Add Hero Slide",
        "cancel_url": reverse("store_admin:heroslide_list"),
    })


@login_required
@staff_required
def heroslide_edit(request, pk):
    slide = get_object_or_404(HeroSlide, pk=pk)
    form = HeroSlideForm(request.POST or None, request.FILES or None, instance=slide)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Hero slide updated successfully.")
        return redirect("store_admin:heroslide_list")
    return render(request, "store_admin/generic_form.html", {
        "form": form,
        "title": "Edit Hero Slide",
        "cancel_url": reverse("store_admin:heroslide_list"),
    })


@login_required
@staff_required
def heroslide_delete(request, pk):
    slide = get_object_or_404(HeroSlide, pk=pk)
    if request.method == "POST":
        slide.delete()
        messages.success(request, "Hero slide deleted.")
        return redirect("store_admin:heroslide_list")
    return render(request, "store_admin/confirm_delete.html", {
        "object": slide,
        "cancel_url": reverse("store_admin:heroslide_list"),
    })


# ── HERO BANNERS ──

@login_required
@staff_required
def herobanner_list(request):
    banners = HeroBanner.objects.all()
    return render(request, "store_admin/herobanner_list.html", {"banners": banners})


@login_required
@staff_required
def herobanner_add(request):
    form = HeroBannerForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Hero banner added successfully.")
        return redirect("store_admin:herobanner_list")
    return render(request, "store_admin/generic_form.html", {
        "form": form,
        "title": "Add Hero Banner",
        "cancel_url": reverse("store_admin:herobanner_list"),
    })


@login_required
@staff_required
def herobanner_edit(request, pk):
    banner = get_object_or_404(HeroBanner, pk=pk)
    form = HeroBannerForm(request.POST or None, request.FILES or None, instance=banner)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Hero banner updated successfully.")
        return redirect("store_admin:herobanner_list")
    return render(request, "store_admin/generic_form.html", {
        "form": form,
        "title": "Edit Hero Banner",
        "cancel_url": reverse("store_admin:herobanner_list"),
    })


@login_required
@staff_required
def herobanner_delete(request, pk):
    banner = get_object_or_404(HeroBanner, pk=pk)
    if request.method == "POST":
        banner.delete()
        messages.success(request, "Hero banner deleted.")
        return redirect("store_admin:herobanner_list")
    return render(request, "store_admin/confirm_delete.html", {
        "object": banner,
        "cancel_url": reverse("store_admin:herobanner_list"),
    })


# ── HOMEPAGE SETTINGS ──

@login_required
@staff_required
def homepage_settings(request):
    settings_obj = HomePageSettings.load()
    form = HomePageSettingsForm(request.POST or None, request.FILES or None, instance=settings_obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Homepage settings updated.")
        return redirect("store_admin:homepage_settings")
    return render(request, "store_admin/generic_form.html", {
        "form": form,
        "title": "Homepage Settings",
    })


# ── ABOUT SECTION ──

@login_required
@staff_required
def about_section(request):
    about = AboutSection.load()
    form = AboutSectionForm(request.POST or None, instance=about)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "About section updated.")
        return redirect("store_admin:about_section")
    return render(request, "store_admin/generic_form.html", {
        "form": form,
        "title": "About Section",
    })


# ── CATEGORIES ──

@login_required
@staff_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, "store_admin/category_list.html", {"categories": categories})


@login_required
@staff_required
def category_add(request):
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Category added successfully.")
        return redirect("store_admin:category_list")
    return render(request, "store_admin/generic_form.html", {
        "form": form,
        "title": "Add Category",
        "cancel_url": reverse("store_admin:category_list"),
    })


@login_required
@staff_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Category updated successfully.")
        return redirect("store_admin:category_list")
    return render(request, "store_admin/generic_form.html", {
        "form": form,
        "title": "Edit Category",
        "cancel_url": reverse("store_admin:category_list"),
    })


@login_required
@staff_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        category.delete()
        messages.success(request, "Category deleted.")
        return redirect("store_admin:category_list")
    return render(request, "store_admin/confirm_delete.html", {
        "object": category,
        "cancel_url": reverse("store_admin:category_list"),
    })


# ── BRANDS ──

@login_required
@staff_required
def brand_list(request):
    brands = Brand.objects.all()
    return render(request, "store_admin/brand_list.html", {"brands": brands})


@login_required
@staff_required
def brand_add(request):
    form = BrandForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Brand added successfully.")
        return redirect("store_admin:brand_list")
    return render(request, "store_admin/generic_form.html", {
        "form": form,
        "title": "Add Brand",
        "cancel_url": reverse("store_admin:brand_list"),
    })


@login_required
@staff_required
def brand_edit(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    form = BrandForm(request.POST or None, request.FILES or None, instance=brand)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Brand updated successfully.")
        return redirect("store_admin:brand_list")
    return render(request, "store_admin/generic_form.html", {
        "form": form,
        "title": "Edit Brand",
        "cancel_url": reverse("store_admin:brand_list"),
    })


@login_required
@staff_required
def brand_delete(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    if request.method == "POST":
        brand.delete()
        messages.success(request, "Brand deleted.")
        return redirect("store_admin:brand_list")
    return render(request, "store_admin/confirm_delete.html", {
        "object": brand,
        "cancel_url": reverse("store_admin:brand_list"),
    })


# ── PRODUCTS ──

@login_required
@staff_required
def product_list(request):
    products = Product.objects.select_related("category", "brand").prefetch_related("skus")
    return render(request, "store_admin/product_list.html", {"products": products})


@login_required
@staff_required
def product_add(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        product = form.save()
        ProductSKU.objects.get_or_create(product=product, variant_combo="", defaults={"stock": 0})
        messages.success(request, "Product added. You can now manage stock and variants.")
        return redirect("store_admin:product_detail", pk=product.pk)
    return render(request, "store_admin/generic_form.html", {
        "form": form,
        "title": "Add Product",
        "cancel_url": reverse("store_admin:product_list"),
    })


@login_required
@staff_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Product updated successfully.")
        return redirect("store_admin:product_detail", pk=product.pk)
    return render(request, "store_admin/generic_form.html", {
        "form": form,
        "title": "Edit Product",
        "cancel_url": reverse("store_admin:product_detail", kwargs={"pk": product.pk}),
    })


@login_required
@staff_required
def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.select_related("category", "brand").prefetch_related(
            "productvariantgroup_set__productvariantoption_set",
            "reviews__user",
        ),
        pk=pk,
    )
    return render(request, "store_admin/product_detail.html", {
        "product": product,
        "skus": product.skus.all(),
        "images": product.images.all(),
        "specs": product.specs.all(),
        "variant_groups": product.productvariantgroup_set.all(),
        "reviews": product.reviews.select_related("user").order_by("-created_at"),
    })


@login_required
@staff_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.delete()
        messages.success(request, "Product deleted.")
        return redirect("store_admin:product_list")
    return render(request, "store_admin/confirm_delete.html", {
        "object": product,
        "cancel_url": reverse("store_admin:product_detail", kwargs={"pk": product.pk}),
    })


# ── PRODUCT SKUs (INVENTORY) ──

@login_required
@staff_required
def sku_add(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    form = ProductSKUForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        sku = form.save(commit=False)
        sku.product = product
        sku.save()
        messages.success(request, "Variant / SKU added.")
        return redirect("store_admin:product_detail", pk=product.pk)
    return render(request, "store_admin/generic_form.html", {
        "form": form,
        "title": f"Add Variant — {product.title}",
        "cancel_url": reverse("store_admin:product_detail", kwargs={"pk": product.pk}),
    })


@login_required
@staff_required
def sku_edit(request, pk):
    sku = get_object_or_404(ProductSKU.objects.select_related("product"), pk=pk)
    form = ProductSKUForm(request.POST or None, instance=sku)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Stock / variant updated.")
        return redirect("store_admin:product_detail", pk=sku.product.pk)
    return render(request, "store_admin/generic_form.html", {
        "form": form,
        "title": f"Edit Variant — {sku.product.title}",
        "cancel_url": reverse("store_admin:product_detail", kwargs={"pk": sku.product.pk}),
    })


@login_required
@staff_required
def sku_delete(request, pk):
    sku = get_object_or_404(ProductSKU.objects.select_related("product"), pk=pk)
    product_pk = sku.product.pk
    if request.method == "POST":
        if sku.product.skus.count() <= 1:
            messages.error(request, "Cannot delete the last variant — every product needs at least one SKU.")
            return redirect("store_admin:product_detail", pk=product_pk)
        sku.delete()
        messages.success(request, "Variant deleted.")
        return redirect("store_admin:product_detail", pk=product_pk)
    return render(request, "store_admin/confirm_delete.html", {
        "object": sku,
        "cancel_url": reverse("store_admin:product_detail", kwargs={"pk": product_pk}),
    })


@login_required
@staff_required
def inventory_list(request):
    skus = ProductSKU.objects.select_related("product").order_by("product__title", "variant_combo")
    return render(request, "store_admin/inventory_list.html", {"skus": skus})


# ── PRODUCT VARIANT GROUPS & OPTIONS ──

@login_required
@staff_required
def variant_group_add(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    form = ProductVariantGroupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        group = form.save(commit=False)
        group.product = product
        group.save()
        messages.success(request, "Variant group added.")
        return redirect("store_admin:product_detail", pk=product.pk)
    return render(request, "store_admin/generic_form.html", {
        "form": form,
        "title": f"Add Variant Group — {product.title}",
        "cancel_url": reverse("store_admin:product_detail", kwargs={"pk": product.pk}),
    })


@login_required
@staff_required
def variant_group_edit(request, pk):
    group = get_object_or_404(ProductVariantGroup.objects.select_related("product"), pk=pk)
    form = ProductVariantGroupForm(request.POST or None, instance=group)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Variant group updated.")
        return redirect("store_admin:product_detail", pk=group.product.pk)
    return render(request, "store_admin/generic_form.html", {
        "form": form,
        "title": f"Edit Variant Group — {group.product.title}",
        "cancel_url": reverse("store_admin:product_detail", kwargs={"pk": group.product.pk}),
    })


@login_required
@staff_required
def variant_group_delete(request, pk):
    group = get_object_or_404(ProductVariantGroup.objects.select_related("product"), pk=pk)
    product_pk = group.product.pk
    if request.method == "POST":
        group.delete()
        messages.success(request, "Variant group deleted.")
        return redirect("store_admin:product_detail", pk=product_pk)
    return render(request, "store_admin/confirm_delete.html", {
        "object": group,
        "cancel_url": reverse("store_admin:product_detail", kwargs={"pk": product_pk}),
    })


@login_required
@staff_required
def variant_option_add(request, group_pk):
    group = get_object_or_404(ProductVariantGroup.objects.select_related("product"), pk=group_pk)
    form = ProductVariantOptionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        option = form.save(commit=False)
        option.group = group
        option.save()
        messages.success(request, "Variant option added.")
        return redirect("store_admin:product_detail", pk=group.product.pk)
    return render(request, "store_admin/generic_form.html", {
        "form": form,
        "title": f"Add Option in {group.name} — {group.product.title}",
        "cancel_url": reverse("store_admin:product_detail", kwargs={"pk": group.product.pk}),
    })


@login_required
@staff_required
def variant_option_edit(request, pk):
    option = get_object_or_404(
        ProductVariantOption.objects.select_related("group", "group__product"),
        pk=pk,
    )
    form = ProductVariantOptionForm(request.POST or None, instance=option)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Variant option updated.")
        return redirect("store_admin:product_detail", pk=option.group.product.pk)
    return render(request, "store_admin/generic_form.html", {
        "form": form,
        "title": f"Edit Option in {option.group.name} — {option.group.product.title}",
        "cancel_url": reverse("store_admin:product_detail", kwargs={"pk": option.group.product.pk}),
    })


@login_required
@staff_required
def variant_option_delete(request, pk):
    option = get_object_or_404(
        ProductVariantOption.objects.select_related("group", "group__product"),
        pk=pk,
    )
    product_pk = option.group.product.pk
    if request.method == "POST":
        option.delete()
        messages.success(request, "Variant option deleted.")
        return redirect("store_admin:product_detail", pk=product_pk)
    return render(request, "store_admin/confirm_delete.html", {
        "object": option,
        "cancel_url": reverse("store_admin:product_detail", kwargs={"pk": product_pk}),
    })


# ── PRODUCT IMAGES ──

@login_required
@staff_required
def product_image_add(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    form = ProductImageForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        image = form.save(commit=False)
        image.product = product
        image.save()
        messages.success(request, "Gallery image added.")
        return redirect("store_admin:product_detail", pk=product.pk)
    return render(request, "store_admin/generic_form.html", {
        "form": form,
        "title": f"Add Gallery Image — {product.title}",
        "cancel_url": reverse("store_admin:product_detail", kwargs={"pk": product.pk}),
    })


@login_required
@staff_required
def product_image_delete(request, pk):
    image = get_object_or_404(ProductImage.objects.select_related("product"), pk=pk)
    product_pk = image.product.pk
    if request.method == "POST":
        image.delete()
        messages.success(request, "Gallery image deleted.")
        return redirect("store_admin:product_detail", pk=product_pk)
    return render(request, "store_admin/confirm_delete.html", {
        "object": image,
        "cancel_url": reverse("store_admin:product_detail", kwargs={"pk": product_pk}),
    })


# ── PRODUCT SPECIFICATIONS ──

@login_required
@staff_required
def product_spec_add(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    form = ProductSpecificationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        spec = form.save(commit=False)
        spec.product = product
        spec.save()
        messages.success(request, "Specification added.")
        return redirect("store_admin:product_detail", pk=product.pk)
    return render(request, "store_admin/generic_form.html", {
        "form": form,
        "title": f"Add Specification — {product.title}",
        "cancel_url": reverse("store_admin:product_detail", kwargs={"pk": product.pk}),
    })


@login_required
@staff_required
def product_spec_edit(request, pk):
    spec = get_object_or_404(ProductSpecification.objects.select_related("product"), pk=pk)
    form = ProductSpecificationForm(request.POST or None, instance=spec)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Specification updated.")
        return redirect("store_admin:product_detail", pk=spec.product.pk)
    return render(request, "store_admin/generic_form.html", {
        "form": form,
        "title": f"Edit Specification — {spec.product.title}",
        "cancel_url": reverse("store_admin:product_detail", kwargs={"pk": spec.product.pk}),
    })


@login_required
@staff_required
def product_spec_delete(request, pk):
    spec = get_object_or_404(ProductSpecification.objects.select_related("product"), pk=pk)
    product_pk = spec.product.pk
    if request.method == "POST":
        spec.delete()
        messages.success(request, "Specification deleted.")
        return redirect("store_admin:product_detail", pk=product_pk)
    return render(request, "store_admin/confirm_delete.html", {
        "object": spec,
        "cancel_url": reverse("store_admin:product_detail", kwargs={"pk": product_pk}),
    })


# ── ORDERS ──

@login_required
@staff_required
def order_list(request):
    orders = Order.objects.select_related("user").all()
    return render(request, "store_admin/order_list.html", {"orders": orders})


@login_required
@staff_required
def order_detail(request, pk):
    order = get_object_or_404(
        Order.objects.select_related("user").prefetch_related("items"),
        pk=pk,
    )

    if request.method == "POST":
        old_status = order.status
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            order.refresh_from_db()
            new_status = order.status

            if old_status != new_status:
                if new_status == Order.STATUS_SHIPPED:
                    send_order_shipped_email.delay(order.pk)
                elif new_status == Order.STATUS_DELIVERED:
                    send_order_delivered_email.delay(order.pk)

            messages.success(request, "Order updated.")
            return redirect("store_admin:order_detail", pk=order.pk)
    else:
        form = OrderStatusForm(instance=order)

    return render(request, "store_admin/order_detail.html", {
        "order": order,
        "form": form,
    })


# ── CUSTOMERS (ACCOUNTS) ──

@login_required
@staff_required
def customer_list(request):
    customers = (
        User.objects.filter(is_superuser=False)
        .select_related("profile")
        .annotate(order_count=Count("orders"))
        .order_by("-date_joined")
    )
    return render(request, "store_admin/customer_list.html", {"customers": customers})


@login_required
@staff_required
def customer_detail(request, pk):
    customer = get_object_or_404(
        User.objects.filter(is_superuser=False).annotate(order_count=Count("orders")),
        pk=pk,
    )
    profile, _ = UserProfile.objects.get_or_create(user=customer)
    return render(request, "store_admin/customer_detail.html", {
        "customer": customer,
        "profile": profile,
        "addresses": customer.addresses.all(),
        "orders": customer.orders.order_by("-created_at")[:20],
    })


@login_required
@staff_required
def customer_edit(request, pk):
    customer = get_object_or_404(User.objects.filter(is_superuser=False), pk=pk)
    profile, _ = UserProfile.objects.get_or_create(user=customer)

    if request.method == "POST":
        form = CustomerForm(request.POST, request.FILES, instance=customer)
    else:
        form = CustomerForm(instance=customer, initial={"phone": profile.phone})

    if request.method == "POST" and form.is_valid():
        user = form.save()
        profile.phone = form.cleaned_data.get("phone", "")
        photo = form.cleaned_data.get("photo")
        if photo is False:
            import os
            if profile.photo and os.path.isfile(profile.photo.path):
                try:
                    os.remove(profile.photo.path)
                except OSError:
                    pass
            profile.photo = None
        elif photo:
            profile.photo = photo
        profile.save()
        messages.success(request, "Customer updated.")
        return redirect("store_admin:customer_detail", pk=user.pk)

    return render(request, "store_admin/generic_form.html", {
        "form": form,
        "title": f"Edit Customer — {customer.username}",
        "cancel_url": reverse("store_admin:customer_detail", kwargs={"pk": customer.pk}),
    })


@login_required
@staff_required
def customer_address_add(request, user_pk):
    customer = get_object_or_404(User.objects.filter(is_superuser=False), pk=user_pk)
    form = CustomerAddressForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        address = form.save(commit=False)
        address.user = customer
        address.save()
        messages.success(request, "Address added.")
        return redirect("store_admin:customer_detail", pk=customer.pk)
    return render(request, "store_admin/generic_form.html", {
        "form": form,
        "title": f"Add Address — {customer.username}",
        "cancel_url": reverse("store_admin:customer_detail", kwargs={"pk": customer.pk}),
    })


@login_required
@staff_required
def customer_address_edit(request, pk):
    address = get_object_or_404(Address.objects.select_related("user"), pk=pk)
    if address.user.is_superuser:
        messages.error(request, "Cannot edit this account.")
        return redirect("store_admin:customer_list")
    form = CustomerAddressForm(request.POST or None, instance=address)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Address updated.")
        return redirect("store_admin:customer_detail", pk=address.user.pk)
    return render(request, "store_admin/generic_form.html", {
        "form": form,
        "title": f"Edit Address — {address.user.username}",
        "cancel_url": reverse("store_admin:customer_detail", kwargs={"pk": address.user.pk}),
    })


@login_required
@staff_required
def customer_address_delete(request, pk):
    address = get_object_or_404(Address.objects.select_related("user"), pk=pk)
    user_pk = address.user.pk
    if address.user.is_superuser:
        messages.error(request, "Cannot delete this account's address.")
        return redirect("store_admin:customer_list")
    if request.method == "POST":
        address.delete()
        messages.success(request, "Address deleted.")
        return redirect("store_admin:customer_detail", pk=user_pk)
    return render(request, "store_admin/confirm_delete.html", {
        "object": address,
        "cancel_url": reverse("store_admin:customer_detail", kwargs={"pk": user_pk}),
    })


# ── SUPPORT (CONTACT + NEWSLETTER) ──


@login_required
@staff_required
def contact_message_list(request):
    contact_messages = ContactMessage.objects.select_related("user").all()
    return render(request, "store_admin/contact_message_list.html", {
        "contact_messages": contact_messages,
    })


@login_required
@staff_required
def contact_message_detail(request, pk):
    contact_msg = get_object_or_404(
        ContactMessage.objects.select_related("user"),
        pk=pk,
    )
    if contact_msg.status == ContactMessage.STATUS_NEW:
        contact_msg.status = ContactMessage.STATUS_READ
        contact_msg.save(update_fields=["status", "updated_at"])
    return render(request, "store_admin/contact_message_detail.html", {
        "contact_msg": contact_msg,
    })


@login_required
@staff_required
def contact_message_mark_read(request, pk):
    contact_msg = get_object_or_404(ContactMessage, pk=pk)
    if request.method == "POST":
        contact_msg.status = ContactMessage.STATUS_READ
        contact_msg.save(update_fields=["status"])
        messages.success(request, "Message marked as read.")
    return redirect("store_admin:contact_message_list")


@login_required
@staff_required
def contact_message_delete(request, pk):
    contact_msg = get_object_or_404(ContactMessage, pk=pk)
    if request.method == "POST":
        contact_msg.delete()
        messages.success(request, "Message deleted.")
        return redirect("store_admin:contact_message_list")
    return render(request, "store_admin/confirm_delete.html", {
        "object": contact_msg,
        "cancel_url": reverse("store_admin:contact_message_list"),
    })


@login_required
@staff_required
def newsletter_subscriber_list(request):
    subscribers = NewsletterSubscriber.objects.all().order_by("-subscribed_at")
    return render(request, "store_admin/newsletter_subscriber_list.html", {
        "subscribers": subscribers,
    })


@login_required
@staff_required
def newsletter_subscriber_toggle_active(request, pk):
    subscriber = get_object_or_404(NewsletterSubscriber, pk=pk)
    if request.method == "POST":
        subscriber.is_active = not subscriber.is_active
        subscriber.save(update_fields=["is_active"])
        messages.success(
            request,
            "Subscriber activated." if subscriber.is_active else "Subscriber deactivated.",
        )
    return redirect("store_admin:newsletter_subscriber_list")


# ── PRODUCT REVIEWS ──


@login_required
@staff_required
def product_review_list(request):
    reviews = ProductReview.objects.select_related("product", "user").order_by("-created_at")
    product_id = request.GET.get("product")
    if product_id:
        reviews = reviews.filter(product_id=product_id)
    return render(request, "store_admin/product_review_list.html", {
        "reviews": reviews,
        "filter_product_id": product_id,
    })


@login_required
@staff_required
def product_review_detail(request, pk):
    review = get_object_or_404(
        ProductReview.objects.select_related("product", "user"),
        pk=pk,
    )
    return render(request, "store_admin/product_review_detail.html", {
        "review": review,
    })


@login_required
@staff_required
def product_review_edit(request, pk):
    review = get_object_or_404(
        ProductReview.objects.select_related("product", "user"),
        pk=pk,
    )
    form = ProductReviewAdminForm(request.POST or None, instance=review)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Review updated successfully.")
        return redirect("store_admin:product_review_detail", pk=review.pk)
    return render(request, "store_admin/generic_form.html", {
        "form": form,
        "title": f"Edit Review — {review.product.title}",
        "cancel_url": reverse("store_admin:product_review_detail", kwargs={"pk": review.pk}),
    })


@login_required
@staff_required
def product_review_toggle_publish(request, pk):
    review = get_object_or_404(ProductReview, pk=pk)
    if request.method == "POST":
        review.is_published = not review.is_published
        review.save(update_fields=["is_published", "updated_at"])
        status = "published" if review.is_published else "hidden"
        messages.success(request, f"Review is now {status}.")
    next_url = request.POST.get("next")
    if next_url:
        return redirect(next_url)
    return redirect("store_admin:product_review_detail", pk=review.pk)


@login_required
@staff_required
def product_review_delete(request, pk):
    review = get_object_or_404(ProductReview.objects.select_related("product"), pk=pk)
    if request.method == "POST":
        review.delete()
        messages.success(request, "Review deleted.")
        return redirect("store_admin:product_review_list")
    return render(request, "store_admin/confirm_delete.html", {
        "object": review,
        "cancel_url": reverse("store_admin:product_review_detail", kwargs={"pk": review.pk}),
    })


@login_required
@staff_required
def newsletter_subscriber_delete(request, pk):
    subscriber = get_object_or_404(NewsletterSubscriber, pk=pk)
    if request.method == "POST":
        subscriber.delete()
        messages.success(request, "Subscriber deleted.")
        return redirect("store_admin:newsletter_subscriber_list")
    return render(request, "store_admin/confirm_delete.html", {
        "object": subscriber,
        "cancel_url": reverse("store_admin:newsletter_subscriber_list"),
    })
