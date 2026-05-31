from django import template

register = template.Library()


def _star_parts(rating):
    try:
        value = float(rating)
    except (TypeError, ValueError):
        value = 0.0
    value = max(0.0, min(5.0, value))
    full = int(value)
    half = 1 if value - full >= 0.25 and full < 5 else 0
    if value - int(value) >= 0.75 and full < 5:
        full += 1
        half = 0
    empty = 5 - full - half
    return full, half, empty


@register.inclusion_tag("products/includes/star_rating.html")
def star_rating(rating, size="md"):
    full, half, empty = _star_parts(rating)
    return {
        "full": range(full),
        "half": range(half),
        "empty": range(empty),
        "size": size,
    }
