from decimal import Decimal, InvalidOperation

from django.db.models import Max, Min, Q

from .models import Brand, Category, Product

SORT_OPTIONS = {
    "newest": ("Newest", "-created_at"),
    "price_asc": ("Price: Low to High", "price"),
    "price_desc": ("Price: High to Low", "-price"),
    "name": ("Name: A–Z", "title"),
}


def _parse_decimal(value):
    if not value:
        return None
    try:
        return Decimal(value)
    except (InvalidOperation, TypeError):
        return None


def _get_descendants(category):
    descendants = [category]
    for child in category.children.prefetch_related('children'):
        descendants.extend(_get_descendants(child))
    return descendants


def build_catalog_queryset(
    *,
    category_slug=None,
    brand_slug=None,
    extra_category_slug=None,
    query="",
    brand_slugs=None,
    min_price=None,
    max_price=None,
    in_stock_only=False,
    on_sale_only=False,
    product_type="",
    sort="newest",
):
    """Return filtered queryset and metadata for the catalog page."""
    qs = Product.objects.select_related("category", "brand")
    active_category = None
    active_brand = None

    if category_slug:
        active_category = Category.objects.filter(slug=category_slug).first()
        if active_category:
            descendants = _get_descendants(active_category)
            qs = qs.filter(category__in=descendants)
    elif extra_category_slug:
        active_category = Category.objects.filter(slug=extra_category_slug).first()
        if active_category:
            descendants = _get_descendants(active_category)
            qs = qs.filter(category__in=descendants)

    if brand_slug:
        active_brand = Brand.objects.filter(slug=brand_slug, is_active=True).first()
        if active_brand:
            qs = qs.filter(brand=active_brand)

    facet_qs = qs

    query = (query or "").strip()
    if query:
        qs = qs.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
            | Q(brand__name__icontains=query)
        )
        facet_qs = qs

    brand_slugs = [s for s in (brand_slugs or []) if s]
    if brand_slugs and not brand_slug:
        qs = qs.filter(brand__slug__in=brand_slugs, brand__is_active=True)

    min_p = _parse_decimal(min_price)
    max_p = _parse_decimal(max_price)
    if min_p is not None:
        qs = qs.filter(price__gte=min_p)
    if max_p is not None:
        qs = qs.filter(price__lte=max_p)

    if in_stock_only:
        qs = qs.filter(stock=True)

    if on_sale_only:
        qs = qs.filter(old_price__isnull=False, old_price__gt=0)

    if product_type:
        qs = qs.filter(product_type=product_type)

    order = SORT_OPTIONS.get(sort, SORT_OPTIONS["newest"])[1]
    qs = qs.order_by(order)

    price_stats = facet_qs.aggregate(
        min_price=Min("price"),
        max_price=Max("price"),
    )

    return {
        "queryset": qs,
        "facet_queryset": facet_qs,
        "active_category": active_category,
        "active_brand": active_brand,
        "query": query,
        "price_stats": price_stats,
        "selected_brand_slugs": brand_slugs,
    }
