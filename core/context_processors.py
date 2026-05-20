def store_defaults(request):
    """Shared template context for layout (nav categories, cart placeholders)."""
    return {
        "categories": getattr(request, "_store_categories", None)
        or [
            {"name": "Mobile phones", "slug": "mobile"},
            {"name": "Laptops", "slug": "laptops"},
            {"name": "Desktop PC", "slug": "desktop"},
            {"name": "Monitors", "slug": "monitors"},
            {"name": "Audio Device", "slug": "audio"},
            {"name": "Printers", "slug": "printers"},
            {"name": "Accessories", "slug": "accessories"},
            {"name": "Graphics Cards", "slug": "gpu"},
            {"name": "SSD Drive", "slug": "ssd"},
            {"name": "Drones", "slug": "drones"},
        ],
        "cart_count": 0,
        "cart_total": "0.00",
        "wishlist_count": 0,
    }
