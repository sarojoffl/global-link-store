from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    path("", views.product_list, name="list"),
    path("category/<slug:category_slug>/", views.product_list, name="category"),
    path("brand/<slug:brand_slug>/", views.product_list, name="brand"),
    path("compare/", views.product_compare, name="compare"),
    path("<slug:slug>/", views.product_detail, name="detail"),
]
