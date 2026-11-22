from django.contrib import admin
from .models import SearchDocument


# Настройки управления документами глобального поиска
@admin.register(SearchDocument)
class SearchDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'entity_type', 'entity_id', 'updated_at')
    list_filter = ('entity_type',)
    search_fields = ('title', 'search_text')
    ordering = ('-updated_at',)