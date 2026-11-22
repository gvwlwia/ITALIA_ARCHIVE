
"""Получение, фильтрация, сохранение и индексирование новостей."""

import html
from datetime import timedelta

from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.html import strip_tags

from apps.content.models import ContentItem
from apps.content.services.sources import fetch_feed
from apps.content.services.importers import generate_unique_slug
from apps.news.models import NewsSource, NewsItem, NewsUpdateLog
from apps.search.models import SearchDocument


# Максимальный возраст новости для импорта
NEWS_MAX_AGE_DAYS = 365

# Тематические слова для предварительного отбора публикаций
RELEVANT_KEYWORDS = (
    'architecture',
    'architectural',
    'building',
    'buildings',
    'restoration',
    'renovation',
    'heritage',
    'historic',
    'historical',
    'museum',
    'urban',
    'monument',
    'palace',
    'church',
    'cathedral',
    'villa',
    'design',
    'project',
    'construction',
    'conservation',
    'colosseum',
    'brunelleschi',
    'carlo scarpa',
    'biennale',
    'архитектур',
    'реставрац',
    'реконструкц',
    'здан',
    'памятник',
    'музей',
    'дворец',
    'собор',
)

# Признаки публикаций об иностранных павильонах
FOREIGN_PAVILION_KEYWORDS = (
    'national pavilion',
    'pavilion of ',
    'pavilion for ',
)

# Упоминания Венеции и её архитектурных площадок
VENICE_KEYWORDS = (
    'venice',
    'venezia',
    'giardini',
    'arsenale',
    'venice architecture biennale',
    'biennale architettura',
)


def clean_news_text(value):
    """Удаляет HTML-разметку и лишние пробелы из текста новости."""

    if not value:
        return ''

    text = strip_tags(value)
    text = html.unescape(text)

    return ' '.join(text.split())


def is_recent_news(data):
    """Проверяет, опубликована ли новость за последние 12 месяцев."""

    published_at = data.get('published_at')

    # Без даты публикации невозможно проверить возраст новости
    if not published_at:
        return False

    # Приводим дату к часовому поясу проекта
    if timezone.is_naive(published_at):
        published_at = timezone.make_aware(
            published_at,
            timezone.get_current_timezone(),
        )

    date_limit = timezone.now() - timedelta(days=NEWS_MAX_AGE_DAYS)

    return published_at >= date_limit


def is_relevant_news(source, data):
    """Проверяет предварительную тематическую и географическую релевантность."""

    title = clean_news_text(data.get('title')).lower()
    summary = clean_news_text(data.get('summary')).lower()

    text = f'{title} {summary}'

    # Проверяем связь публикации с архитектурой
    if not any(keyword in text for keyword in RELEVANT_KEYWORDS):
        return False

    source_name = source.name.lower()

    # Для ленты Венеции дополнительно отсекаем материалы
    # об иностранных национальных павильонах
    if 'venice' in source_name or 'venezia' in source_name:
        is_foreign_pavilion = any(
            keyword in text
            for keyword in FOREIGN_PAVILION_KEYWORDS
        )

        concerns_venice = any(
            keyword in text
            for keyword in VENICE_KEYWORDS
        )

        if is_foreign_pavilion and not concerns_venice:
            return False

    # Ленты ArchDaily привязаны к конкретным городам Италии.
    # Поэтому географическую принадлежность предварительно
    # определяем по названию зарегистрированного источника.
    return True


def is_suitable_news(source, data):
    """Объединяет проверки даты и тематики."""

    return (
        is_recent_news(data)
        and is_relevant_news(source, data)
    )


def preview_news(source=None):
    """
    Проверяет RSS-ленты без сохранения публикаций в базе.
    Возвращает количество подходящих и неподходящих новостей.
    """

    if source is not None:
        sources = NewsSource.objects.filter(
            pk=source.pk,
            is_active=True,
        )
    else:
        sources = NewsSource.objects.filter(is_active=True)

    results = []

    for news_source in sources:
        try:
            publications = fetch_feed(news_source.feed_url)

            suitable = [
                item for item in publications
                if is_suitable_news(news_source, item)
            ]

            results.append({
                'source': news_source.name,
                'found': len(publications),
                'suitable': len(suitable),
                'skipped': len(publications) - len(suitable),
                'error': '',
            })

        except Exception as error:
            results.append({
                'source': news_source.name,
                'found': 0,
                'suitable': 0,
                'skipped': 0,
                'error': str(error)[:500],
            })

    return results


@transaction.atomic
def save_news(source, data):
    """Сохраняет одну новость и добавляет её в поисковый индекс."""

    title = (data.get('title') or '').strip()
    original_url = (data.get('original_url') or '').strip()
    external_id = (data.get('external_id') or '').strip()

    summary = clean_news_text(data.get('summary'))

    # Проверяем обязательные сведения
    if not title or not original_url:
        return False

    if not original_url.startswith(('http://', 'https://')):
        return False

    # Повторно проверяем дату и тематику перед сохранением
    if not is_suitable_news(source, data):
        return False

    # Проверяем, не импортирована ли новость ранее
    if NewsItem.objects.filter(original_url=original_url).exists():
        return False

    if external_id and NewsItem.objects.filter(
        source=source,
        external_id=external_id,
    ).exists():
        return False

    if not summary:
        summary = 'Описание новости отсутствует.'

    published_at = data.get('published_at')

    # Создаём общую запись материала
    content_item = ContentItem.objects.create(
        content_type='news',
        title=title,
        slug=generate_unique_slug(title, original_url),
        summary=summary,
        source_url=original_url,
        source_name=source.name,
        published_at=published_at,
        status='draft',
    )

    # Создаём специализированную запись новости
    news_item = NewsItem.objects.create(
        content_item=content_item,
        source=source,
        original_url=original_url,
        external_id=external_id or None,
        source_published_at=published_at,
    )

    # Формируем поисковую запись
    search_text = ' '.join([
        title,
        summary,
        source.name,
    ])

    SearchDocument.objects.update_or_create(
        entity_type='news',
        entity_id=news_item.news_id,
        defaults={
            'title': title,
            'search_text': search_text,
        },
    )

    return True


def update_news(source=None):
    """
    Обновляет новости из одного или всех активных источников.
    Импортирует только подходящие публикации за последние 12 месяцев.
    """

    if source is not None:
        sources = NewsSource.objects.filter(
            pk=source.pk,
            is_active=True,
        )
    else:
        sources = NewsSource.objects.filter(is_active=True)

    sources_checked = sources.count()

    total_found = 0
    total_added = 0
    total_failed = 0

    for news_source in sources:
        # Создаём запись о начале обновления
        log = NewsUpdateLog.objects.create(
            source=news_source,
            status='running',
        )

        try:
            # Получаем публикации из RSS-ленты
            publications = fetch_feed(news_source.feed_url)

            items_found = len(publications)
            items_added = 0

            # Отбираем и сохраняем только подходящие новости
            for publication in publications:
                if not is_suitable_news(news_source, publication):
                    continue

                try:
                    if save_news(news_source, publication):
                        items_added += 1

                except IntegrityError:
                    # Пропускаем публикацию при конфликте уникальности
                    continue

            # Сохраняем результаты обновления
            log.items_found = items_found
            log.items_added = items_added
            log.status = 'success'

            total_found += items_found
            total_added += items_added

        except Exception as error:
            # Фиксируем ошибку, не прерывая остальные источники
            log.status = 'failed'
            log.error_message = str(error)[:5000]

            total_failed += 1

        finally:
            # Запоминаем время последней проверки
            news_source.last_checked_at = timezone.now()
            news_source.save(update_fields=['last_checked_at'])

            # Завершаем запись в журнале
            log.finished_at = timezone.now()
            log.save(update_fields=[
                'items_found',
                'items_added',
                'status',
                'error_message',
                'finished_at',
            ])

    return {
        'sources_checked': sources_checked,
        'items_found': total_found,
        'items_added': total_added,
        'sources_failed': total_failed,
    }
