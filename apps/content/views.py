
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import ContentItem, ObjectContentLink


def content_home(request):
    """Отображает главную страницу раздела материалов."""

    # Считаем опубликованные статьи и новости, выбранные для раздела статей
    articles_count = ContentItem.objects.filter(
        Q(content_type='article') |
        Q(content_type='news', show_in_articles=True),
        status='published'
    ).count()

    # Считаем опубликованные изображения
    images_count = ContentItem.objects.filter(
        content_type='image',
        status='published'
    ).count()

    # Считаем опубликованные видеоматериалы
    videos_count = ContentItem.objects.filter(
        content_type='video',
        status='published'
    ).count()

    # Передаём количество материалов в HTML-шаблон
    context = {
        'articles_count': articles_count,
        'images_count': images_count,
        'videos_count': videos_count,
    }

    return render(
        request,
        'content/content_home.html',
        context
    )


def articles_list(request):
    """Отображает опубликованные статьи и выбранные новости."""

    articles = (
        ContentItem.objects
        .filter(
            Q(content_type='article') |
            Q(content_type='news', show_in_articles=True),
            status='published'
        )
        .select_related('article')
        .order_by('-published_at', 'title')
    )

    return render(request, 'content/articles_list.html', {
        'articles': articles
    })


def article_detail(request, slug):
    """Отображает подробную страницу статьи или выбранной новости."""

    article = get_object_or_404(
        ContentItem.objects
        .filter(
            Q(content_type='article') |
            Q(content_type='news', show_in_articles=True),
            status='published'
        )
        .select_related('article'),
        slug=slug
    )

    return render(request, 'content/article_detail.html', {
        'article': article
    })


def images_list(request):
    # Получаем опубликованные фотографии, связанные с объектами
    links = (
        ObjectContentLink.objects
        .filter(
            link_type='depicts',
            content_item__content_type='image',
            content_item__status='published'
        )
        .select_related(
            'architectural_object',
            'content_item',
            'content_item__media'
        )
        .order_by(
            'architectural_object__name',
            'content_item_id'
        )
    )

    # Объединяем фотографии по архитектурным объектам
    grouped_images = {}

    for link in links:
        obj = link.architectural_object

        if obj.pk not in grouped_images:
            grouped_images[obj.pk] = {
                'object': obj,
                'photos': []
            }

        grouped_images[obj.pk]['photos'].append(link.content_item)

    context = {
        'image_groups': list(grouped_images.values())
    }

    return render(
        request,
        'content/images_list.html',
        context
    )


def videos_list(request):
    """Отображает список опубликованных видеоматериалов."""

    videos = (
        ContentItem.objects
        .filter(content_type='video', status='published')
        .select_related('media')
        .order_by('-published_at', 'title')
    )

    return render(request, 'content/videos_list.html', {
        'videos': videos
    })
