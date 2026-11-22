
from django.db.models import Q, Prefetch
from django.shortcuts import render, get_object_or_404

from .models import ArchitecturalObject
from apps.content.models import ObjectContentLink


# Локальные фотографии для карточек объектов в каталоге.
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
    .select_related(
        'content_item',
        'content_item__media'
    )
    .order_by('link_id')
)


# Все опубликованные фотографии для подробной страницы объекта.
# Здесь учитываются локальные файлы и изображения Wikimedia Commons.
detail_images = (
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
    .select_related(
        'content_item',
        'content_item__media'
    )
    .order_by('link_id')
)


def catalog_list(request):
    """Отображает список опубликованных архитектурных объектов."""

    # Получаем объекты вместе со справочниками и локальными фотографиями.
    objects = (
        ArchitecturalObject.objects
        .filter(is_published=True)
        .prefetch_related(
            'city_links__city',
            'style_links__style',
            'epoch_links__epoch',
            'architect_links__architect',
            Prefetch(
                'content_links',
                queryset=object_images,
                to_attr='image_links'
            )
        )
        .order_by('name')
    )

    return render(
        request,
        'catalog/catalog_list.html',
        {'objects': objects}
    )


def object_detail(request, slug):
    """Отображает подробную информацию об архитектурном объекте."""

    # Находим опубликованный объект по его уникальному адресу.
    # Для подробной страницы загружаем все опубликованные фотографии.
    architectural_object = get_object_or_404(
        ArchitecturalObject.objects
        .filter(is_published=True)
        .prefetch_related(
            'city_links__city',
            'style_links__style',
            'epoch_links__epoch',
            'architect_links__architect',
            'tag_links__tag',
            Prefetch(
                'content_links',
                queryset=detail_images,
                to_attr='image_links'
            )
        ),
        slug=slug
    )

    # Передаём объект и связанные фотографии в шаблон страницы.
    return render(
        request,
        'catalog/object_detail.html',
        {'object': architectural_object}
    )
