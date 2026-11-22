
from django.contrib import admin
from .models import (
    ContentItem,
    Article,
    Media,
    Tag,
    ContentItemTag,
    ObjectContentLink,
    CityContentLink
)

# Общие настройки отображения материалов
@admin.register(ContentItem)
class ContentItemAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'content_type',
        'status',
        'show_in_articles',
        'created_at',
        'published_at'
    )

    list_filter = (
        'content_type',
        'status',
        'show_in_articles'
    )

    search_fields = ('title', 'summary')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-created_at',)

    # Поля, доступные для редактирования в карточке материала
    fields = (
        'content_type',
        'title',
        'slug',
        'summary',
        'source_url',
        'source_name',
        'license_info',
        'show_in_articles',
        'status',
        'published_at'
    )


# Настройки отображения статей
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('content_item', 'author')
    search_fields = ('content_item__title', 'author')


# Настройки изображений и видео
@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):

    # Какие сведения показывать в общем списке
    list_display = (
        'content_item',
        'media_type',
        'media_source',
        'external_id',
        'file_url'
    )

    # Фильтрация по типу и источнику материала
    list_filter = (
        'media_type',
        'media_source'
    )

    # Поиск по названию, подписи и внешнему идентификатору
    search_fields = (
        'content_item__title',
        'caption',
        'external_id'
    )

    # Поля, доступные при редактировании материала
    fields = (
        'content_item',
        'media_type',
        'media_source',
        'external_id',
        'image_file',
        'file_url',
        'alt_text',
        'caption'
    )


# Настройки тегов
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)


# Настройки связей материалов с тегами
@admin.register(ContentItemTag)
class ContentItemTagAdmin(admin.ModelAdmin):
    list_display = ('content_item', 'tag')
    search_fields = ('content_item__title', 'tag__name')


# Настройки связей материалов с архитектурными объектами
@admin.register(ObjectContentLink)
class ObjectContentLinkAdmin(admin.ModelAdmin):
    list_display = ('architectural_object', 'content_item', 'link_type')
    list_filter = ('link_type',)
    search_fields = ('architectural_object__name', 'content_item__title')


# Настройки связей видеоматериалов с городами
@admin.register(CityContentLink)
class CityContentLinkAdmin(admin.ModelAdmin):
    list_display = ('city', 'content_item')
    list_filter = ('city',)
    search_fields = ('city__name', 'content_item__title')