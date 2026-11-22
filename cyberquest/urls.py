"""Root URL configuration for CyberQuest."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls")),
    path("learning/", include("apps.learning.urls")),
    path("challenges/", include("apps.challenges.urls")),
    path("", include("apps.core.urls")),
]

# Local development only. static() is a no-op when DEBUG is False, so
# production deployments must serve MEDIA_ROOT/MEDIA_URL themselves.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
