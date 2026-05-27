from django.conf import settings
from django.db import models
from django.utils import timezone


class HeroSlide(models.Model):
    PLACEMENT_CHOICES = (
        ("left", "Left slider"),
        ("right", "Right slider"),
    )
    MEDIA_CHOICES = (
        ("image", "Image"),
        ("video", "Video file"),
    )

    placement = models.CharField(
        max_length=10,
        choices=PLACEMENT_CHOICES,
        default="left",
        help_text="Which hero slider this slide appears in.",
    )
    media_type = models.CharField(
        max_length=10,
        choices=MEDIA_CHOICES,
        default="image",
    )
    image = models.ImageField(upload_to="hero/", blank=True, null=True)
    video = models.FileField(
        upload_to="hero/videos/",
        blank=True,
        null=True,
        help_text="MP4/WebM video file (used when media type is Video).",
    )
    url = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["placement", "order", "id"]

    def __str__(self):
        label = self.get_placement_display()
        kind = self.get_media_type_display()
        return f"{label} — {kind} (#{self.pk})"

    @property
    def has_media(self):
        if self.media_type == "video":
            return bool(self.video)
        return bool(self.image)


class HomePageSettings(models.Model):
    """Singleton homepage options (background, etc.)."""

    top_zone_background = models.ImageField(
        upload_to="home/backgrounds/",
        blank=True,
        null=True,
        help_text="Background image behind hero sliders and brand strip (up to Popular Categories).",
    )

    class Meta:
        verbose_name = "Homepage settings"
        verbose_name_plural = "Homepage settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Homepage settings"


class AboutSection(models.Model):
    """Singleton about block with animated stats for the homepage."""

    title = models.CharField(max_length=255, default="About Global Link Store")
    heading = models.CharField(
        max_length=255,
        default="Quality laptops, phones & electronics — delivered across Nepal",
    )
    description = models.TextField(
        default=(
            "Global Link Store is your trusted online destination for laptops, "
            "smartphones, desktops, and accessories. We partner with leading brands "
            "and focus on genuine products, fair pricing, and reliable support."
        )
    )
    products_listed = models.PositiveIntegerField(
        default=500,
        help_text="Shown in stats counter (e.g. products available).",
    )
    orders_delivered = models.PositiveIntegerField(
        default=1200,
        help_text="Shown in stats counter.",
    )
    happy_customers = models.PositiveIntegerField(
        default=850,
        help_text="Shown in stats counter.",
    )
    years_of_service = models.PositiveIntegerField(
        default=5,
        help_text="Years in business — counter animates to this number.",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "About section"
        verbose_name_plural = "About section"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    STATUS_NEW = "new"
    STATUS_READ = "read"
    STATUS_ARCHIVED = "archived"
    STATUS_CHOICES = [
        (STATUS_NEW, "New"),
        (STATUS_READ, "Read"),
        (STATUS_ARCHIVED, "Archived"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contact_messages",
    )

    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True, default="")
    subject = models.CharField(max_length=150)
    message = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} — {self.email}"


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=120, blank=True, default="")
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    subscribed_at = models.DateTimeField(default=timezone.now)
    last_subscribed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-subscribed_at"]

    def __str__(self):
        return self.email
