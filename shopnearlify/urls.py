from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path(
        "admin/",
        admin.site.urls,
        name="admin",
    ),
    path("accounts/", include("allauth.urls")),
    path("", include("store.urls")),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
    path("ratings/", include("star_ratings.urls", namespace="ratings")),
    path("", include("paystack_api.urls")),
    path("", include("delivery.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
