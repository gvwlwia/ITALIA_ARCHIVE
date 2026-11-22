from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('apps.core.urls')),
    path('catalog/', include('apps.catalog.urls')),
    path('references/', include('apps.references.urls')),
    path('content/', include('apps.content.urls')),
    path('news/', include('apps.news.urls')),
    path('search/', include('apps.search.urls')),
    path('graph/', include('apps.graph.urls')),
]

# Настройка отображения загруженных файлов при разработке
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )