from django.core.paginator import Paginator
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, render
from .models import BlogCategory, BlogPost


def blog_list(request):
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()

    posts = BlogPost.objects.filter(is_published=True).select_related("category", "author")
    active_category = None

    if category_slug:
        active_category = get_object_or_404(BlogCategory, slug=category_slug)
        posts = posts.filter(category=active_category)

    if query:
        posts = posts.filter(
            Q(title__icontains=query) | Q(excerpt__icontains=query) | Q(content__icontains=query)
        )

    categories = BlogCategory.objects.all()
    recent_posts = BlogPost.objects.filter(is_published=True).order_by("-created_at")[:5]

    paginator = Paginator(posts, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "posts": page_obj,
        "page_obj": page_obj,
        "categories": categories,
        "active_category": active_category,
        "query": query,
        "recent_posts": recent_posts,
    }
    return render(request, "blog/blog_list.html", context)


def blog_category(request, category_slug):
    category = get_object_or_404(BlogCategory, slug=category_slug)
    posts = BlogPost.objects.filter(is_published=True, category=category).select_related("category", "author")

    paginator = Paginator(posts, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    categories = BlogCategory.objects.all()
    recent_posts = BlogPost.objects.filter(is_published=True).order_by("-created_at")[:5]

    context = {
        "posts": page_obj,
        "page_obj": page_obj,
        "categories": categories,
        "active_category": category,
        "recent_posts": recent_posts,
    }
    return render(request, "blog/blog_list.html", context)


def blog_detail(request, slug):
    post = get_object_or_404(
        BlogPost.objects.select_related("category", "author").prefetch_related("featured_products"),
        slug=slug,
        is_published=True,
    )

    # Increment view count
    BlogPost.objects.filter(pk=post.pk).update(view_count=F("view_count") + 1)
    post.refresh_from_db(fields=["view_count"])

    related_posts = (
        BlogPost.objects.filter(is_published=True)
        .exclude(pk=post.pk)
        .filter(category=post.category)
        .order_by("-created_at")[:3]
    )

    context = {
        "post": post,
        "related_posts": related_posts,
        "featured_products": post.featured_products.all(),
    }
    return render(request, "blog/blog_detail.html", context)
