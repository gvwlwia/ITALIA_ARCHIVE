
"""Представления глобального поиска ITALIA ARCHIVE."""

import re

from django.db.models import Q, Prefetch
from django.shortcuts import render

from apps.catalog.models import ArchitecturalObject
from apps.content.models import ContentItem, ObjectContentLink
from apps.references.models import City, Style, Epoch, Architect


# Русские и английские названия городов и архитектурных направлений.
SEARCH_SYNONYM_GROUPS = [
    ('рим', 'rome'),
    ('венеция', 'venice'),
    ('флоренция', 'florence'),
    ('милан', 'milan'),
    ('неаполь', 'naples'),
    ('турин', 'turin'),
    ('болонья', 'bologna'),
    ('генуя', 'genoa'),
    ('пиза', 'pisa'),
    ('верона', 'verona'),
    ('палермо', 'palermo'),
    ('барокко', 'baroque'),
    ('ренессанс', 'renaissance', 'возрождение'),
    ('готика', 'gothic'),
    ('романский стиль', 'romanesque'),
    ('классицизм', 'neoclassicism'),
    ('модернизм', 'modernism'),
    ('футуризм', 'futurism'),
    ('античность', 'antiquity'),
]


# Категории, доступные в глобальном поиске.
# Статьи и теги исключены.
SEARCH_CATEGORIES = [
    ('objects', 'Объекты'),
    ('images', 'Фото'),
    ('videos', 'Видео'),
    ('news', 'Новости'),
    ('cities', 'Города'),
    ('styles', 'Стили'),
    ('epochs', 'Эпохи'),
    ('architects', 'Архитекторы'),
]


# Локальные фотографии для каталога и карточек объектов.
# Внешние изображения здесь не используются.
object_images = (
    ObjectContentLink.objects
    .filter(
        link_type='depicts',
        content_item__content_type='image',
        content_item__status='published',
        content_item__media__media_type='image',
        content_item__media__media_source='local',
    )
    .exclude(content_item__media__image_file='')
    .select_related('content_item', 'content_item__media')
    .order_by('link_id')
)


# Все опубликованные фотографии для отдельной категории «Фото».
# Здесь учитываются локальные файлы и внешние изображения.
search_object_images = (
    ObjectContentLink.objects
    .filter(
        link_type='depicts',
        content_item__content_type='image',
        content_item__status='published',
        content_item__media__media_type='image',
    )
    .filter(
        Q(content_item__media__image_file__gt='') |
        Q(content_item__media__file_url__gt='')
    )
    .select_related('content_item', 'content_item__media')
    .order_by('link_id')
)


def get_search_variants(query):
    """Возвращает исходный запрос и его известные языковые варианты."""

    variants = {query}
    normalized_query = query.lower()

    for group in SEARCH_SYNONYM_GROUPS:
        for term in group:
            pattern = r'(?<!\w)' + re.escape(term) + r'(?!\w)'

            if re.search(pattern, normalized_query):
                for alternative in group:
                    if alternative != term:
                        translated_query = re.sub(
                            pattern,
                            alternative,
                            query,
                            flags=re.IGNORECASE,
                        )
                        variants.add(translated_query)

    return list(variants)


def build_search_query(terms, fields):
    """Создаёт условие поиска по нескольким словам и полям."""

    query_filter = Q()

    for term in terms:
        for field in fields:
            query_filter |= Q(**{f'{field}__icontains': term})

    return query_filter


def get_objects_with_galleries(queryset, include_external=False):
    """
    Добавляет к объектам фотографии для индивидуальных каруселей.

    Для обычных карточек используются только локальные фотографии.
    Для категории «Фото» разрешены также внешние изображения.
    """

    # Выбираем подходящий набор фотографий.
    images_queryset = (
        search_object_images if include_external else object_images
    )

    return queryset.prefetch_related(
        'city_links__city',
        'style_links__style',
        'epoch_links__epoch',
        'architect_links__architect',
        Prefetch(
            'content_links',
            queryset=images_queryset,
            to_attr='image_links',
        ),
    )


def global_search(request):
    """Выполняет глобальный поиск и фильтрацию результатов."""

    query = request.GET.get('q', '').strip()
    active_type = request.GET.get('type', 'all')

    valid_types = ['all'] + [
        key for key, label in SEARCH_CATEGORIES
    ]

    if active_type not in valid_types:
        active_type = 'all'

    # Подготавливаем категории результатов.
    results = {
        'objects': [],
        'images': [],
        'videos': [],
        'news': [],
        'cities': [],
        'styles': [],
        'epochs': [],
        'architects': [],
    }

    if query:
        search_terms = get_search_variants(query)

        # 1. Условия поиска архитектурных объектов.
        object_filter = build_search_query(
            search_terms,
            [
                'name',
                'description',
                'object_type',
                'address',
                'city_links__city__name',
                'style_links__style__name',
                'epoch_links__epoch__name',
                'architect_links__architect__full_name',
            ],
        )

        published_objects = ArchitecturalObject.objects.filter(
            is_published=True
        )

        # 2. Общие условия поиска по фотографиям и видео.
        # Учитываем связанные объекты и их города.
        content_filter = build_search_query(
            search_terms,
            [
                'title',
                'summary',
                'source_name',
                'media__caption',
                'media__alt_text',
                'object_links__architectural_object__name',
                'object_links__architectural_object__description',
                'object_links__architectural_object__city_links__city__name',
            ],
        )

        # 3. Находим локальные и внешние фотографии.
        matching_images = (
            ContentItem.objects
            .filter(
                content_filter,
                content_type='image',
                status='published',
                media__media_type='image',
            )
            .filter(
                Q(media__image_file__gt='') |
                Q(media__file_url__gt='')
            )
            .distinct()
        )

        # Получаем ID объектов, к которым привязаны фотографии.
        image_object_ids = (
            matching_images
            .filter(object_links__link_type='depicts')
            .values_list(
                'object_links__architectural_object_id',
                flat=True,
            )
            .distinct()
        )

        # 4. Архитектурные объекты.
        # Ищем по собственным данным и связанным фотографиям.
        matched_objects = (
            published_objects
            .filter(
                Q(object_filter) | Q(pk__in=image_object_ids)
            )
            .distinct()
            .order_by('name')
        )

        # В обычных карточках объектов показываем только локальные фото.
        results['objects'] = get_objects_with_galleries(
            matched_objects
        )[:20]


        # 5. Категория «Фото».
        # Ищем фотографии независимо от результатов категории «Объекты».
        # Это позволяет находить и локальные, и внешние изображения.

        image_content_filter = build_search_query(
            search_terms,
            [
                'content_links__content_item__title',
                'content_links__content_item__summary',
                'content_links__content_item__source_name',
                'content_links__content_item__media__caption',
                'content_links__content_item__media__alt_text',
            ],
        )

        image_objects = (
            ArchitecturalObject.objects
            .filter(
                is_published=True,
                content_links__link_type='depicts',
                content_links__content_item__content_type='image',
                content_links__content_item__status='published',
                content_links__content_item__media__media_type='image',
            )
            .filter(
                Q(object_filter) | Q(image_content_filter)
            )
            .filter(
                Q(
                    content_links__content_item__media__image_file__gt=''
                ) |
                Q(
                    content_links__content_item__media__file_url__gt=''
                )
            )
            .distinct()
            .order_by('name')
        )

        # В этой категории показываем локальные и внешние фотографии.
        results['images'] = get_objects_with_galleries(
            image_objects,
            include_external=True,
        )[:20]


        # 6. Видеоматериалы.
        # Определяем города найденных архитектурных объектов.
        matched_city_ids = (
            matched_objects
            .values_list('city_links__city_id', flat=True)
            .distinct()
        )

        # Ищем видео по собственным данным, объектам и городам.
        video_filter = (
            content_filter |
            Q(city_links__city_id__in=matched_city_ids)
        )

        results['videos'] = (
            ContentItem.objects
            .filter(
                video_filter,
                content_type='video',
                status='published',
                media__media_type='video',
            )
            .exclude(media__file_url__isnull=True)
            .exclude(media__file_url='')
            .select_related('media')
            .distinct()
            .order_by('title')[:20]
        )

        # 7. Новости.
        results['news'] = (
            ContentItem.objects
            .filter(
                content_filter,
                content_type='news',
                status='published',
            )
            .distinct()
            .order_by('-published_at')[:20]
        )

        # 8. Города.
        results['cities'] = (
            City.objects
            .filter(
                build_search_query(search_terms, ['name'])
            )
            .order_by('name')[:20]
        )

        # 9. Архитектурные стили.
        results['styles'] = (
            Style.objects
            .filter(
                build_search_query(
                    search_terms,
                    ['name', 'description'],
                )
            )
            .order_by('name')[:20]
        )

        # 10. Исторические эпохи.
        results['epochs'] = (
            Epoch.objects
            .filter(
                build_search_query(
                    search_terms,
                    ['name', 'description'],
                )
            )
            .order_by('name')[:20]
        )

        # 11. Архитекторы.
        results['architects'] = (
            Architect.objects
            .filter(
                build_search_query(
                    search_terms,
                    ['full_name', 'country', 'biography'],
                )
            )
            .order_by('full_name')[:20]
        )

    # Подсчитываем количество результатов в каждой категории.
    result_counts = {
        key: len(results[key])
        for key, label in SEARCH_CATEGORIES
    }

    all_total_results = sum(result_counts.values())

    # Формируем вкладки фильтрации.
    category_filters = [
        {
            'key': 'all',
            'label': 'Всё',
            'count': all_total_results,
        }
    ]

    for key, label in SEARCH_CATEGORIES:
        category_filters.append({
            'key': key,
            'label': label,
            'count': result_counts[key],
        })

    # Оставляем результаты выбранной категории.
    if active_type == 'all':
        visible_results = results
    else:
        visible_results = {
            active_type: results[active_type]
        }

    total_results = sum(
        len(items) for items in visible_results.values()
    )

    context = {
        'query': query,
        'results': visible_results,
        'total_results': total_results,
        'all_total_results': all_total_results,
        'category_filters': category_filters,
        'active_type': active_type,
    }

    return render(
        request,
        'search/search.html',
        context,
    )
