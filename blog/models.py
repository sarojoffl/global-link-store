from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify


class BlogCategory(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Blog Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            qs = BlogCategory.objects.all()
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            while qs.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:category", kwargs={"category_slug": self.slug})


class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, max_length=255)
    category = models.ForeignKey(
        BlogCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="posts"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="blog_posts"
    )
    featured_image = models.ImageField(upload_to="blog/", blank=True, null=True)
    excerpt = models.TextField(blank=True, help_text="Short summary for cards and search snippets (150-250 characters)")
    content = models.TextField(help_text="Full article body. Supports HTML tags and formatting.")
    meta_title = models.CharField(max_length=150, blank=True, help_text="SEO Title for Google (leave empty to use Title)")
    meta_description = models.CharField(max_length=255, blank=True, help_text="SEO Description for Google SERP")
    featured_products = models.ManyToManyField(
        "products.Product", blank=True, related_name="blog_mentions", help_text="Products recommended in this guide to display as interactive buy cards"
    )
    faq_data = models.JSONField(
        default=list, blank=True, help_text='List of FAQ items e.g. [{"question": "Is 8GB RAM enough?", "answer": "Yes for office work..."}]'
    )
    is_published = models.BooleanField(default=True, db_index=True)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            qs = BlogPost.objects.all()
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            while qs.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        if not self.meta_title:
            self.meta_title = self.title[:150]
        if not self.meta_description and self.excerpt:
            self.meta_description = self.excerpt[:250]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:detail", kwargs={"slug": self.slug})

    @property
    def reading_time(self):
        word_count = len(self.content.split())
        minutes = max(1, round(word_count / 200))
        return minutes
