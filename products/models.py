from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, blank=True)
    icon = models.CharField(max_length=100, blank=True)
    is_popular = models.BooleanField(default=False)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            # Exclude current category if it has an id (updating)
            qs = Category.objects.all()
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            while qs.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def is_root(self):
        return self.parent is None

    @property
    def has_grandchildren(self):
        """Returns True if any of this category's children have children of their own (meaning it needs a mega-menu)."""
        return self.children.filter(children__isnull=False).exists()

    @property
    def total_products_count(self):
        """Returns the count of products in this category and all its descendants."""
        from products.catalog import _get_descendants
        descendants = _get_descendants(self)
        return Product.objects.filter(category__in=descendants).count()


class Brand(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, blank=True)
    logo = models.ImageField(upload_to='brands/')
    url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    PRODUCT_TYPES = (
        ("featured", "Featured"),
        ("offer", "Best Offer"),
        ("new", "New Arrival"),
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    old_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to="products/")
    description = models.TextField(blank=True)
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def is_in_stock(self):
        """True if any SKU has stock > 0."""
        return self.skus.filter(stock__gt=0).exists()

    @property
    def discount_percent(self):
        if self.old_price and self.price:
            return int(((self.old_price - self.price) / self.old_price) * 100)
        return 0

    @property
    def save_amount(self):
        if self.old_price and self.price:
            return self.old_price - self.price
        return 0


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/gallery/")
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.title} Image"


class ProductVariantGroup(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.product.title} — {self.name}"


class ProductVariantOption(models.Model):
    group = models.ForeignKey(ProductVariantGroup, on_delete=models.CASCADE)
    value = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.group.name}: {self.value}"


class ProductSpecification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="specs")
    section = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=255)
    is_key = models.BooleanField(
        default=False,
        help_text="Show this spec in the key specs section on the product page.",
    )

    class Meta:
        ordering = ["section", "name"]

    def __str__(self):
        return f"{self.name}: {self.value}"


class ProductSKU(models.Model):
    """
    Represents a specific purchasable combination of variant options.
    e.g. iPhone 16 — Color:Black,Variant:8GB+128GB

    Products with no variants have a single SKU with variant_combo="".
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="skus")
    variant_combo = models.CharField(
        max_length=255,
        blank=True,
        help_text='Comma-separated key:value pairs. e.g. "Color:Black,Variant:8GB+128GB"',
    )
    stock = models.PositiveIntegerField(default=0)
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ["product", "variant_combo"]
        ordering = ["variant_combo"]

    @property
    def is_in_stock(self):
        return self.stock > 0

    @property
    def display_name(self):
        return self.variant_combo.replace(",", " / ") if self.variant_combo else "Default"

    def __str__(self):
        return f"{self.product.title} — {self.display_name} (stock: {self.stock})"


class ProductReview(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="product_reviews",
    )
    rating = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=120)
    body = models.TextField()
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["product", "user"],
                name="unique_review_per_user_product",
            ),
        ]

    def __str__(self):
        return f"{self.product.title} — {self.rating}★ by {self.user}"