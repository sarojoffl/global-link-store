from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from .forms import ContactForm, NewsletterForm
from .models import AboutSection, HeroSlide, HomePageSettings, ContactMessage, NewsletterSubscriber
from products.models import Product, Category, Brand


def _active_hero_slides(placement):
    return HeroSlide.objects.filter(
        active=True,
        placement=placement,
    ).filter(
        Q(media_type="image", image__isnull=False)
        | Q(media_type="video", video__isnull=False)
    ).order_by("order", "id")


@ensure_csrf_cookie
def index(request):
    context = {
        "query": request.GET.get("q", ""),

        "home_settings": HomePageSettings.load(),
        "about_section": AboutSection.load(),
        "hero_slides_left": _active_hero_slides("left"),
        "hero_slides_right": _active_hero_slides("right"),

        "popular_categories": Category.objects.filter(
            is_popular=True
        )[:7],

        # Latest by created date
        "latest_products": Product.objects.order_by(
            "-created_at"
        )[:8],

        # Product type sections
        "featured_products": Product.objects.filter(
            product_type="featured"
        )[:8],

        "best_offers": Product.objects.filter(
            product_type="offer"
        )[:8],

        "new_arrivals": Product.objects.filter(
            product_type="new"
        )[:8],

        "brands": Brand.objects.filter(
            is_active=True
        ).order_by("order"),
    }

    return render(request, "core/index.html", context)


@ensure_csrf_cookie
def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_msg: ContactMessage = form.save(commit=False)
            contact_msg.user = request.user if request.user.is_authenticated else None
            contact_msg.ip_address = request.META.get("REMOTE_ADDR")
            contact_msg.save()
            messages.success(request, "Thanks! Your message has been received. We'll get back to you soon.")
            return redirect("core:contact")
    else:
        form = ContactForm()

    return render(request, "core/contact.html", {"form": form})


@require_POST
@ensure_csrf_cookie
def newsletter_subscribe(request):
    form = NewsletterForm(request.POST)
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if form.is_valid():
        email = form.cleaned_data["email"].strip().lower()
        name = (form.cleaned_data.get("name") or "").strip()
        now = timezone.now()

        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=email,
            defaults={
                "name": name,
                "is_active": True,
                "subscribed_at": now,
                "last_subscribed_at": now,
            },
        )
        if not created:
            if name:
                subscriber.name = name
            subscriber.is_active = True
            subscriber.subscribed_at = now
            subscriber.last_subscribed_at = now
            subscriber.save()

        msg = "You’re subscribed! Watch your inbox for updates."
        if is_ajax:
            return JsonResponse({"ok": True, "message": msg})
        messages.success(request, msg)
        return redirect(request.META.get("HTTP_REFERER") or reverse("core:index"))

    error = " ".join(form.errors.get("email", ["Please enter a valid email address."]))
    if is_ajax:
        return JsonResponse({"ok": False, "error": error}, status=400)
    messages.error(request, error)
    return redirect(request.META.get("HTTP_REFERER") or reverse("core:index"))