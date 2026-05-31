from django.db.models import Avg, Count, Sum

from shop.models import Order, OrderItem

from .models import ProductReview


COMPLETED_ORDER_STATUSES = (
    Order.STATUS_CONFIRMED,
    Order.STATUS_SHIPPED,
    Order.STATUS_DELIVERED,
)


def get_verified_purchaser_ids(product):
    return set(
        OrderItem.objects.filter(
            product=product,
            order__status__in=COMPLETED_ORDER_STATUSES,
            order__user__isnull=False,
        ).values_list("order__user_id", flat=True)
    )


def get_product_sold_count(product):
    total = (
        OrderItem.objects.filter(
            product=product,
            order__status__in=COMPLETED_ORDER_STATUSES,
        ).aggregate(total=Sum("quantity"))["total"]
    )
    return total or 0


def get_product_review_context(product):
    reviews_qs = (
        ProductReview.objects.filter(product=product, is_published=True)
        .select_related("user")
        .order_by("-created_at")
    )
    review_count = reviews_qs.count()
    avg_rating = reviews_qs.aggregate(avg=Avg("rating"))["avg"]

    distribution = {star: 0 for star in range(5, 0, -1)}
    for row in reviews_qs.values("rating").annotate(count=Count("id")):
        distribution[row["rating"]] = row["count"]

    distribution_rows = []
    for star in range(5, 0, -1):
        count = distribution[star]
        percent = round((count / review_count) * 100) if review_count else 0
        distribution_rows.append(
            {"star": star, "count": count, "percent": percent}
        )

    verified_ids = get_verified_purchaser_ids(product)
    reviews = []
    for review in reviews_qs:
        reviews.append(
            {
                "review": review,
                "is_verified": review.user_id in verified_ids,
            }
        )

    return {
        "reviews": reviews,
        "review_count": review_count,
        "avg_rating": round(float(avg_rating), 1) if avg_rating is not None else None,
        "rating_distribution": distribution_rows,
        "sold_count": get_product_sold_count(product),
    }
