from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from manage_user.admin import custom_admin_site

urlpatterns = [

    # Custom Admin Panel
    path("admin/", custom_admin_site.urls),

    # Authentication & User Management (root level)
    path("", include("manage_user.urls")),

    # Core Service App
    path("manage_service/", include("manage_service.urls")),

    # Chat System
    path("chat/", include("chat.urls")),

    # Payments
    path("payments/", include("payments.urls")),
]

# Media Files (Development Only)
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )