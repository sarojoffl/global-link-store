from django import template
from django.http import QueryDict

register = template.Library()


@register.simple_tag(takes_context=True)
def catalog_query(context, **updates):
    """Build a query string preserving current GET params with optional overrides."""
    request = context.get("request")
    if not request:
        return ""

    q = request.GET.copy()
    for key, value in updates.items():
        if value is None or value == "":
            q.pop(key, None)
        elif isinstance(value, list):
            q.setlist(key, value)
        else:
            q[key] = value

    qs = q.urlencode()
    return "?" + qs if qs else ""
