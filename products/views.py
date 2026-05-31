from collections import defaultdict
from itertools import product
import json

from django.core.paginator import Paginator
from django.db.models import Count, Prefetch
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .catalog import SORT_OPTIONS, build_catalog_queryset
from .compare_utils import build_comparison_rows, get_compare_products, parse_compare_ids
from .forms import ProductReviewForm
from .models import Brand, Category, Product, ProductReview, ProductVariantGroup, ProductVariantOption
from .review_utils import get_product_review_context
from django.core.serializers.json import DjangoJSONEncoder
from .utils import format_variant_combo


def _catalog_base_url(request, active_category=None, active_brand=None):
    if active_category and not active_brand:
        return request.build_absolute_uri(
            request.resolver_match.url_name == "products:category"
            and request.path
            or f"/products/category/{active_category.slug}/"
        )
    if active_brand and not active_category:
        return f"/products/brand/{active_brand.slug}/"
    return "/products/"


def product_list(request, category_slug=None, brand_slug=None):
    query = request.GET.get("q", "").strip()
    extra_category = request.GET.get("category", "").strip()
    brand_slugs = list(request.GET.getlist("brand"))
    single_brand = request.GET.get("brand", "").strip()
    if single_brand and single_brand not in brand_slugs:
        brand_slugs.append(single_brand)
    min_price = request.GET.get("min_price", "")
    max_price = request.GET.get("max_price", "")
    in_stock = request.GET.get("in_stock") == "1"
    on_sale = request.GET.get("on_sale") == "1"
    product_type = request.GET.get("type", "").strip()
    sort = request.GET.get("sort", "newest").strip()

    if sort not in SORT_OPTIONS:
        sort = "newest"

    catalog = build_catalog_queryset(
        category_slug=category_slug,
        brand_slug=brand_slug,
        extra_category_slug=extra_category if not category_slug else None,
        query=query,
        brand_slugs=brand_slugs,
        min_price=min_price,
        max_price=max_price,
        in_stock_only=in_stock,
        on_sale_only=on_sale,
        product_type=product_type,
        sort=sort,
    )

    products_qs = catalog["queryset"]
    facet_qs = catalog["facet_queryset"]
    active_category = catalog["active_category"]
    active_brand = catalog["active_brand"]

    filter_brand = active_brand
    if not filter_brand and brand_slugs:
        filter_brand = Brand.objects.filter(
            slug=brand_slugs[0], is_active=True
        ).first()

    paginator = Paginator(products_qs, 12)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    # Sidebar facets
    categories = (
        Category.objects.annotate(product_count=Count("product"))
        .filter(product_count__gt=0)
        .order_by("name")
    )

    brand_filters = (
        Brand.objects.filter(is_active=True, product__in=facet_qs)
        .annotate(product_count=Count("product", distinct=True))
        .filter(product_count__gt=0)
        .order_by("order", "name")
    )

    price_stats = catalog["price_stats"]
    price_min_bound = price_stats.get("min_price")
    price_max_bound = price_stats.get("max_price")

    # Page title & breadcrumbs
    if query:
        page_title = f'Search results for "{query}"'
        page_subtitle = f"{paginator.count} product{'s' if paginator.count != 1 else ''} found"
    elif active_category and (active_brand or filter_brand):
        brand_name = (active_brand or filter_brand).name
        page_title = f"{brand_name} — {active_category.name}"
        page_subtitle = f"Shop {brand_name} {active_category.name.lower()}"
    elif active_category:
        page_title = active_category.name
        page_subtitle = f"Browse all {active_category.name.lower()}"
    elif active_brand:
        page_title = f"{active_brand.name} Products"
        page_subtitle = f"All products from {active_brand.name}"
    else:
        page_title = "All Products"
        page_subtitle = "Browse our full catalog"

    # Canonical list URL for forms
    if category_slug:
        form_action = request.path
    elif brand_slug:
        form_action = request.path
    else:
        form_action = "/products/"

    has_active_filters = bool(
        brand_slugs
        or min_price
        or max_price
        or in_stock
        or on_sale
        or product_type
        or (extra_category and not category_slug)
    )

    context = {
        "page_obj": page_obj,
        "products": page_obj.object_list,
        "paginator": paginator,
        "query": query,
        "active_category": active_category,
        "active_brand": active_brand,
        "filter_brand": filter_brand,
        "categories": categories,
        "brand_filters": brand_filters,
        "selected_brand_slugs": catalog["selected_brand_slugs"],
        "min_price": min_price,
        "max_price": max_price,
        "price_min_bound": price_min_bound,
        "price_max_bound": price_max_bound,
        "in_stock": in_stock,
        "on_sale": on_sale,
        "product_type": product_type,
        "sort": sort,
        "sort_options": [(k, v[0]) for k, v in SORT_OPTIONS.items()],
        "page_title": page_title,
        "page_subtitle": page_subtitle,
        "form_action": form_action,
        "has_active_filters": has_active_filters,
        "total_count": paginator.count,
        "product_types": Product.PRODUCT_TYPES,
    }

    return render(request, "products/product_list.html", context)


@ensure_csrf_cookie
def product_detail(request, slug):
    variant_groups_qs = ProductVariantGroup.objects.prefetch_related(
        Prefetch(
            "productvariantoption_set",
            queryset=ProductVariantOption.objects.order_by("id"),
        )
    )

    product = get_object_or_404(
        Product.objects.select_related("category", "brand").prefetch_related(
            "images",
            "specs",
            Prefetch("productvariantgroup_set", queryset=variant_groups_qs),
        ),
        slug=slug,
    )

    gallery = [{"url": product.image.url, "alt": product.title}]
    for img in product.images.order_by("order", "id"):
        gallery.append({"url": img.image.url, "alt": product.title})

    specs_by_section = defaultdict(list)
    for spec in product.specs.all().order_by("section", "name"):
        specs_by_section[spec.section].append(spec)

    key_specs = list(
        product.specs.filter(is_key=True).order_by("section", "name")[:6]
    )
    if not key_specs:
        key_specs = list(product.specs.all().order_by("section", "name")[:6])

    variant_groups = list(product.productvariantgroup_set.all())

    related_products = (
        Product.objects.filter(category=product.category)
        .exclude(pk=product.pk)
        .select_related("category", "brand")[:12]
    )

    sku_data = [
        {
            "variant_combo": sku.variant_combo,
            "display_combo": format_variant_combo(sku.variant_combo),
            "stock": sku.stock,
            "price_adjustment": sku.price_adjustment,
        }
        for sku in product.skus.all()
    ]

    product_in_wishlist = False
    user_has_reviewed = False
    if request.user.is_authenticated:
        product_in_wishlist = request.user.wishlist_items.filter(
            product=product
        ).exists()
        user_has_reviewed = ProductReview.objects.filter(
            product=product,
            user=request.user,
        ).exists()

    review_context = get_product_review_context(product)

    return render(
        request,
        "products/product_detail.html",
        {
            "product": product,
            "gallery": gallery,
            "specs_by_section": dict(specs_by_section),
            "key_specs": key_specs,
            "variant_groups": variant_groups,
            "related_products": related_products,
            "sku_data_json": json.dumps(sku_data, cls=DjangoJSONEncoder),
            "product_in_wishlist": product_in_wishlist,
            "user_has_reviewed": user_has_reviewed,
            "review_form": ProductReviewForm(),
            **review_context,
        },
    )


@login_required
@require_POST
def submit_review(request, slug):
    product = get_object_or_404(Product, slug=slug)

    if ProductReview.objects.filter(product=product, user=request.user).exists():
        return JsonResponse(
            {"ok": False, "error": "You have already reviewed this product."},
            status=400,
        )

    form = ProductReviewForm(request.POST)
    if not form.is_valid():
        first_error = next(iter(form.errors.values()))[0]
        return JsonResponse({"ok": False, "error": first_error}, status=400)

    review = form.save(commit=False)
    review.product = product
    review.user = request.user
    review.save()

    stats = get_product_review_context(product)
    return JsonResponse(
        {
            "ok": True,
            "message": "Thank you! Your review has been published.",
            "review_count": stats["review_count"],
            "avg_rating": stats["avg_rating"],
        }
    )


def product_compare(request):
    id_list = parse_compare_ids(request.GET.get("ids", ""))
    products = get_compare_products(id_list)
    rows = build_comparison_rows(products)

    return render(
        request,
        "products/compare.html",
        {
            "products": products,
            "rows": rows,
            "compare_ids": ",".join(str(p.pk) for p in products),
        },
    )


def search_autocomplete(request):
    query = request.GET.get("q", "").strip()
    results = []
    if len(query) >= 2:
        products = Product.objects.filter(title__icontains=query).select_related("category", "brand")[:8]
        for p in products:
            results.append({
                "id": p.id,
                "title": p.title,
                "price": str(p.price),
                "url": f"/products/{p.slug}/",
                "image": p.image.url if p.image else "",
                "category": p.category.name,
                "brand": p.brand.name if p.brand else "",
            })
    return JsonResponse({"results": results})