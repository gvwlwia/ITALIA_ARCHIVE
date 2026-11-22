
import json

from django.shortcuts import render
from django.urls import reverse

from apps.catalog.models import (
    ArchitecturalObject,
    ObjectCity,
    ObjectStyle,
    ObjectEpoch,
    ObjectArchitect,
)
from apps.references.models import City, Style, Epoch, Architect


def graph_view(request):
    """Формирует данные для интерактивного графа архитектуры Италии."""

    nodes = []
    edges = []

    # Добавляем только опубликованные архитектурные объекты
    objects = ArchitecturalObject.objects.filter(
        is_published=True
    )

    # Добавляем узлы архитектурных объектов
    for obj in objects:
        nodes.append({
            'id': f'object_{obj.object_id}',
            'label': obj.name,
            'group': 'object',
            'title': obj.name,
            'url': reverse(
                'catalog:object_detail',
                kwargs={'slug': obj.slug}
            ),
        })

    # Получаем идентификаторы опубликованных объектов
    object_ids = objects.values_list('object_id', flat=True)

    # Добавляем города и связи с архитектурными объектами
    city_links = ObjectCity.objects.filter(
        architectural_object_id__in=object_ids
    ).select_related('city', 'architectural_object')

    for link in city_links:
        city = link.city

        nodes.append({
            'id': f'city_{city.city_id}',
            'label': city.name,
            'group': 'city',
            'title': f'{city.name}, {city.region}',
        })

        edges.append({
            'from': f'object_{link.architectural_object_id}',
            'to': f'city_{city.city_id}',
            'label': 'расположен в',
        })

    # Добавляем архитектурные стили и связи
    style_links = ObjectStyle.objects.filter(
        architectural_object_id__in=object_ids
    ).select_related('style', 'architectural_object')

    for link in style_links:
        style = link.style

        nodes.append({
            'id': f'style_{style.style_id}',
            'label': style.name,
            'group': 'style',
            'title': style.name,
        })

        edges.append({
            'from': f'object_{link.architectural_object_id}',
            'to': f'style_{style.style_id}',
            'label': 'стиль',
        })

    # Добавляем исторические эпохи и связи
    epoch_links = ObjectEpoch.objects.filter(
        architectural_object_id__in=object_ids
    ).select_related('epoch', 'architectural_object')

    for link in epoch_links:
        epoch = link.epoch

        nodes.append({
            'id': f'epoch_{epoch.epoch_id}',
            'label': epoch.name,
            'group': 'epoch',
            'title': epoch.name,
        })

        edges.append({
            'from': f'object_{link.architectural_object_id}',
            'to': f'epoch_{epoch.epoch_id}',
            'label': 'эпоха',
        })

    # Добавляем архитекторов и связи с объектами
    architect_links = ObjectArchitect.objects.filter(
        architectural_object_id__in=object_ids
    ).select_related('architect', 'architectural_object')

    for link in architect_links:
        architect = link.architect

        nodes.append({
            'id': f'architect_{architect.architect_id}',
            'label': architect.full_name,
            'group': 'architect',
            'title': architect.full_name,
        })

        edges.append({
            'from': f'object_{link.architectural_object_id}',
            'to': f'architect_{architect.architect_id}',
            'label': link.role or 'архитектор',
        })

    # Убираем повторяющиеся узлы
    unique_nodes = {
        node['id']: node
        for node in nodes
    }

    context = {
        'graph_nodes': json.dumps(
            list(unique_nodes.values()),
            ensure_ascii=False
        ),
        'graph_edges': json.dumps(
            edges,
            ensure_ascii=False
        ),
    }

    return render(
        request,
        'graph/graph.html',
        context
    )
