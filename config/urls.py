from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('products/', include('products.urls', namespace='products')),
    path('', include('shop.urls', namespace='shop')),
    path('auth/', include('social_django.urls', namespace='social')),    
    path('accounts/', include('accounts.urls', namespace='accounts')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)