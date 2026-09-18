"""
Root URLconf — updated through Phase 3.

feed:home (path '') is the application root per TSD §6.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.feed.urls')),            # feed:home at '/', post URLs
    path('archive/', include('apps.archive.urls')), # Phase 3
    path('links/',   include('apps.linking.urls')), # Phase 4
    path('trust/',   include('apps.trust.urls')),   # Phase 5
    path('', include('apps.users.urls')),           # /register/, /login/, /profile/…
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
