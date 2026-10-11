from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.blog_list, name="list"),
    path("category/<slug:category_slug>/", views.blog_category, name="category"),
    path("<slug:slug>/", views.blog_detail, name="detail"),
]
