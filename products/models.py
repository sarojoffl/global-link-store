from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=120)

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    icon = models.CharField(
        max_length=100,
        blank=True
    )

    is_popular = models.BooleanField(default=False)

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

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

    stock = models.BooleanField(default=True)

    product_type = models.CharField(
        max_length=20,
        choices=PRODUCT_TYPES,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def discount_percent(self):
        if self.old_price and self.price:
            return int(((self.old_price - self.price) / self.old_price) * 100)
        return 0
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/gallery/")
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.title} Image"
    
class ProductVariantGroup(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  # Color / Storage

class ProductVariantOption(models.Model):
    group = models.ForeignKey(ProductVariantGroup, on_delete=models.CASCADE)
    value = models.CharField(max_length=100)
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class ProductSpecification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="specs")
    section = models.CharField(max_length=100)  # GENERAL, DISPLAY, etc
    name = models.CharField(max_length=100)     # RAM, CPU, Battery
    value = models.CharField(max_length=255)

