from django.urls import path
from . import views
 
app_name = "core"

urlpatterns = [
    path('', views.index, name='index'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path("contact/", views.contact, name="contact"),
    path("refund-policy/", views.refund_policy, name="refund_policy"),
    path("terms/", views.terms, name="terms"),
    path(
        "newsletter/subscribe/",
        views.newsletter_subscribe,
        name="newsletter_subscribe",
    ),
]