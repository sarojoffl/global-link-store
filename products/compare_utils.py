"""Build product comparison table data (max 3 products)."""

from .models import Product


def parse_compare_ids(raw: str, max_count=3):
    ids = []
    for part in (raw or "").split(","):
        part = part.strip()
        if part.isdigit():
            ids.append(int(part))
        if len(ids) >= max_count:
            break
    return ids


def get_compare_products(id_list):
    if not id_list:
        return []

    id_list = id_list[:3]
    qs = (
        Product.objects.filter(pk__in=id_list)
        .select_related("category", "brand")
        .prefetch_related("specs")
    )
    by_id = {p.pk: p for p in qs}
    return [by_id[pk] for pk in id_list if pk in by_id]


def build_comparison_rows(products):
    """Return list of {label, values} for template."""
    if not products:
        return []

    rows = []

    def vals(getter):
        return [getter(p) for p in products]

    rows.append({
        "label": "Price",
        "values": vals(lambda p: f"Rs {p.price:,.2f}"),
    })

    rows.append({
        "label": "Brand",
        "values": vals(lambda p: p.brand.name if p.brand else "—"),
    })

    rows.append({
        "label": "Category",
        "values": vals(lambda p: p.category.name),
    })

    rows.append({
        "label": "Availability",
        "values": vals(lambda p: "In stock" if p.is_in_stock else "Out of stock"),
    })

    if any(p.old_price for p in products):
        rows.append({
            "label": "Was price",
            "values": vals(
                lambda p: f"Rs {p.old_price:,.2f}" if p.old_price else "—"
            ),
        })

    spec_keys = []
    seen = set()
    for product in products:
        for spec in product.specs.all():
            key = (spec.section.strip(), spec.name.strip())
            if key not in seen:
                seen.add(key)
                spec_keys.append(key)

    spec_keys.sort(key=lambda k: (k[0].lower(), k[1].lower()))

    spec_map = {}
    for product in products:
        for spec in product.specs.all():
            spec_map[(product.pk, spec.section.strip(), spec.name.strip())] = spec.value

    for section, name in spec_keys:
        label = f"{section} — {name}" if section else name
        rows.append({
            "label": label,
            "values": [
                spec_map.get((p.pk, section, name), "—") for p in products
            ],
        })

    return rows
