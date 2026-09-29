from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include

from products.sitemaps import (
    ProductSitemap,
    CategorySitemap,
    BrandSitemap,
    StaticViewSitemap,
)

sitemaps = {
    "products": ProductSitemap,
    "categories": CategorySitemap,
    "brands": BrandSitemap,
    "static": StaticViewSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'sitemap.xml',
        sitemap,
        {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap',
    ),
    path('', include('core.urls')),
    path('products/', include('products.urls', namespace='products')),
    path('', include('shop.urls', namespace='shop')),
    path('auth/', include('social_django.urls', namespace='social')),    
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path("store-admin/", include("store_admin.urls", namespace="store_admin")),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)