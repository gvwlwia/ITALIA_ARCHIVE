from django.contrib import admin
from .models import City, Style, Epoch, Architect


# Настройки отображения городов в административной панели
@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'region')
    search_fields = ('name', 'region')
    ordering = ('name',)


# Настройки отображения архитектурных стилей
@admin.register(Style)
class StyleAdmin(admin.ModelAdmin):
    list_display = ('name', 'period_start', 'period_end', 'parent_style')
    search_fields = ('name',)
    ordering = ('name',)


# Настройки отображения исторических эпох
@admin.register(Epoch)
class EpochAdmin(admin.ModelAdmin):
    list_display = ('name', 'year_start', 'year_end')
    search_fields = ('name',)
    ordering = ('name',)


# Настройки отображения архитекторов
@admin.register(Architect)
class ArchitectAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'country', 'birth_year', 'death_year')
    search_fields = ('full_name', 'country')
    ordering = ('full_name',)