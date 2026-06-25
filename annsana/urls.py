"""
Root URL configuration for Annsana.

Mirrors the routing table in TSD Section 6. Each app owns its own urls.py;
this file only does top-level dispatch plus dev-mode media serving.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.users.urls')),

    # Added as each phase lands:
    # path('', include('apps.feed.urls')),
    # path('archive/', include('apps.archive.urls')),
    # path('links/', include('apps.linking.urls')),
    # path('trust/', include('apps.trust.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
