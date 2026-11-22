"""Формирование поисковых записей для материалов базы знаний."""

from apps.content.models import Article, Media, ContentItemTag
from apps.search.models import SearchDocument


def index_content_item(content_item):
    """
    Добавляет материал в глобальный поисковый индекс
    или обновляет существующую поисковую запись.
    """

    # Определяем тип материала и его идентификатор
    if content_item.content_type == 'article':
        entity_type = 'article'
        related_item = Article.objects.filter(
            content_item=content_item
        ).first()

        if related_item is None:
            return

        entity_id = related_item.pk
        additional_text = related_item.body
        author = related_item.author or ''

    elif content_item.content_type in ('image', 'video'):
        entity_type = content_item.content_type
        related_item = Media.objects.filter(
            content_item=content_item
        ).first()

        if related_item is None:
            return

        entity_id = related_item.pk
        additional_text = ' '.join([
            related_item.alt_text or '',
            related_item.caption or '',
        ])
        author = ''

    else:
        # Другие типы материалов индексируются отдельно
        return

    # Получаем названия тегов, связанных с материалом
    tag_names = ContentItemTag.objects.filter(
        content_item=content_item
    ).select_related('tag').values_list('tag__name', flat=True)

    # Собираем текст, по которому будет выполняться поиск
    search_parts = [
        content_item.title,
        content_item.summary,
        additional_text,
        author,
        content_item.source_name or '',
        *tag_names,
    ]

    search_text = ' '.join(
        part.strip()
        for part in search_parts
        if part and part.strip()
    )

    # Создаём поисковую запись или обновляем существующую
    SearchDocument.objects.update_or_create(
        entity_type=entity_type,
        entity_id=entity_id,
        defaults={
            'title': content_item.title,
            'search_text': search_text,
        },
    )