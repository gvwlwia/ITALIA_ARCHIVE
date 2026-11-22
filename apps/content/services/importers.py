
"""Сохранение импортированных материалов в базу знаний."""

import hashlib

from django.db import transaction
from django.utils.text import slugify

from apps.content.models import ContentItem, Article, Media


def generate_unique_slug(title, source_url):
    """Создаёт уникальный адрес материала."""

    # Формируем основу адреса из названия
    base_slug = slugify(title) or 'material'

    # Добавляем хеш ссылки на источник
    url_hash = hashlib.sha256(
        source_url.encode('utf-8')
    ).hexdigest()[:12]

    # Ограничиваем длину адреса с учётом хеша
    max_base_length = 255 - len(url_hash) - 1
    base_slug = base_slug[:max_base_length]

    return f'{base_slug}-{url_hash}'


@transaction.atomic
def import_material(
    data,
    material_type,
    source_name,
    license_info='',
):
    """
    Импортирует статью, изображение или видео.

    Возвращает кортеж:
    (объект материала, признак создания новой записи).
    """

    # Проверяем допустимый тип материала
    if material_type not in ('article', 'image', 'video'):
        raise ValueError('Неподдерживаемый тип материала.')

    # Получаем основные сведения
    title = (data.get('title') or '').strip()
    summary = (data.get('summary') or '').strip()
    source_url = (data.get('original_url') or '').strip()

    # Проверяем обязательные поля
    if not title:
        raise ValueError('У материала отсутствует название.')

    if not source_url:
        raise ValueError('У материала отсутствует ссылка на источник.')

    # Проверяем ссылку на источник
    if not source_url.startswith(('http://', 'https://')):
        raise ValueError('Некорректная ссылка на источник.')

    if not summary:
        summary = 'Описание материала отсутствует.'

    # Проверяем, не импортирован ли материал ранее
    existing_item = ContentItem.objects.filter(
        source_url=source_url
    ).first()

    if existing_item:
        return existing_item, False

    # Для изображений и видео заранее проверяем наличие ссылки
    media_url = ''

    if material_type in ('image', 'video'):
        media_url = (data.get('media_url') or '').strip()

        if not media_url:
            raise ValueError(
                'Для изображения или видео необходим media_url.'
            )

        if not media_url.startswith(('http://', 'https://')):
            raise ValueError('Некорректная ссылка на медиафайл.')

    # Подготавливаем общую запись материала
    content_item = ContentItem.objects.create(
        content_type=material_type,
        title=title,
        slug=generate_unique_slug(title, source_url),
        summary=summary,
        source_url=source_url,
        source_name=source_name,
        license_info=license_info,
        published_at=data.get('published_at'),
        status='draft',
    )

    # Сохраняем дополнительную информацию о материале
    if material_type == 'article':
        # Сохраняем текст статьи, если он предоставлен
        # Иначе используем краткое описание как содержимое
        body = (data.get('body') or summary).strip()

        Article.objects.create(
            content_item=content_item,
            body=body,
            author=data.get('author') or None,
        )

    else:
        # Сохраняем сведения об изображении или видео
        Media.objects.create(
            content_item=content_item,
            media_type=material_type,
            file_url=media_url,
            alt_text=data.get('alt_text') or '',
            caption=data.get('caption') or '',
        )

    # Добавляем материал в глобальный поисковый индекс
    from apps.content.services.indexing import index_content_item

    index_content_item(content_item)

    return content_item, True
