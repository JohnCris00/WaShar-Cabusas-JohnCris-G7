from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

handler403 = "accounts.views.permission_denied"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("shops/", include("shops.urls")),
    path("", include("accounts.urls")),
    path("reservations/", include("reservations.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)