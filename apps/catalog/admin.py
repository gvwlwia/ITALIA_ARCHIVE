from django.contrib import admin
from .models import (
    ArchitecturalObject,
    ObjectCity,
    ObjectStyle,
    ObjectEpoch,
    ObjectArchitect,
    ObjectTag,
)


# Настройки отображения архитектурных объектов
@admin.register(ArchitecturalObject)
class ArchitecturalObjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'object_type', 'year_start', 'year_end', 'is_published')
    search_fields = ('name', 'description', 'address')
    list_filter = ('object_type', 'is_published')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)


# Настройки связей объектов с городами
@admin.register(ObjectCity)
class ObjectCityAdmin(admin.ModelAdmin):
    list_display = ('architectural_object', 'city', 'is_primary')
    list_filter = ('is_primary',)
    search_fields = ('architectural_object__name', 'city__name')


# Настройки связей объектов с архитектурными стилями
@admin.register(ObjectStyle)
class ObjectStyleAdmin(admin.ModelAdmin):
    list_display = ('architectural_object', 'style', 'is_primary')
    list_filter = ('is_primary',)
    search_fields = ('architectural_object__name', 'style__name')


# Настройки связей объектов с историческими эпохами
@admin.register(ObjectEpoch)
class ObjectEpochAdmin(admin.ModelAdmin):
    list_display = ('architectural_object', 'epoch', 'is_primary')
    list_filter = ('is_primary',)
    search_fields = ('architectural_object__name', 'epoch__name')


# Настройки связей объектов с архитекторами
@admin.register(ObjectArchitect)
class ObjectArchitectAdmin(admin.ModelAdmin):
    list_display = ('architectural_object', 'architect', 'role')
    search_fields = ('architectural_object__name', 'architect__full_name')


# Настройки связей объектов с тегами
@admin.register(ObjectTag)
class ObjectTagAdmin(admin.ModelAdmin):
    list_display = ('architectural_object', 'tag')
    search_fields = ('architectural_object__name', 'tag__name')