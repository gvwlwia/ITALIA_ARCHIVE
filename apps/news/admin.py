from django.contrib import admin
from .models import NewsSource, NewsItem, NewsUpdateLog


# Настройки управления источниками новостей
@admin.register(NewsSource)
class NewsSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'feed_url', 'is_active', 'last_checked_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'feed_url')
    ordering = ('name',)


# Настройки отображения новостей
@admin.register(NewsItem)
class NewsItemAdmin(admin.ModelAdmin):
    list_display = ('content_item', 'source', 'source_published_at', 'fetched_at')
    list_filter = ('source',)
    search_fields = ('content_item__title', 'original_url')
    ordering = ('-fetched_at',)


# Настройки журнала обновления новостей
@admin.register(NewsUpdateLog)
class NewsUpdateLogAdmin(admin.ModelAdmin):
    list_display = ('started_at', 'finished_at', 'source', 'status', 'items_found', 'items_added')
    list_filter = ('status', 'source')
    ordering = ('-started_at',)