from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from products.models import Product, Category, Brand


class ProductSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Product.objects.all().order_by("-created_at")

    def lastmod(self, obj):
        return obj.created_at


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Category.objects.all().order_by("name")


class BrandSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Brand.objects.filter(is_active=True)


class StaticViewSitemap(Sitemap):
    priority = 0.6
    changefreq = "monthly"

    def items(self):
        return [
            "core:index",
            "core:contact",
            "core:refund_policy",
            "core:terms",
            "products:list",
        ]

    def location(self, item):
        return reverse(item)
