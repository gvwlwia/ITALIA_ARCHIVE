
"""
Получение фотографий из Wikimedia Commons
для проекта ITALIA ARCHIVE.
"""

import json
import re
from html import unescape
from urllib.parse import urlencode
from urllib.request import Request, urlopen


# Адрес API Wikimedia Commons.
WIKIMEDIA_API_URL = 'https://commons.wikimedia.org/w/api.php'

# Представляем приложение при обращении к API.
USER_AGENT = 'ITALIA_ARCHIVE/1.0 (Django educational project)'


def clean_metadata(value):
    """Удаляет HTML-разметку из описаний и данных об авторстве."""

    if not value:
        return ''

    # Некоторые поля API содержат HTML-разметку.
    value = re.sub(r'<[^>]+>', '', str(value))

    return unescape(value).strip()


def get_metadata_value(metadata, key):
    """Получает значение одного поля из метаданных изображения."""

    field = metadata.get(key, {})

    if isinstance(field, dict):
        return clean_metadata(field.get('value', ''))

    return clean_metadata(field)


def fetch_commons_images(search_query, limit=10):
    """
    Ищет фотографии в Wikimedia Commons.

    Возвращает список изображений с URL, авторством,
    лицензией и ссылкой на страницу оригинала.
    """

    # Формируем параметры запроса к API.
    params = {
        'action': 'query',
        'format': 'json',
        'generator': 'search',
        'gsrsearch': search_query,
        'gsrnamespace': 6,
        'gsrlimit': min(max(int(limit), 1), 50),
        'prop': 'imageinfo',
        'iiprop': 'url|extmetadata',
        'iiurlwidth': 1200,
    }

    request_url = (
        WIKIMEDIA_API_URL
        + '?'
        + urlencode(params)
    )

    request = Request(
        request_url,
        headers={
            'User-Agent': USER_AGENT,
        },
    )

    try:
        # Отправляем запрос и получаем ответ API.
        with urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode('utf-8'))

    except Exception as error:
        raise RuntimeError(
            f'Не удалось получить данные Wikimedia Commons: {error}'
        ) from error

    pages = data.get('query', {}).get('pages', {})

    images = []

    # Обрабатываем найденные изображения.
    for page in pages.values():

        image_info_list = page.get('imageinfo', [])

        if not image_info_list:
            continue

        image_info = image_info_list[0]
        metadata = image_info.get('extmetadata', {})

        # Получаем сведения об авторе и лицензии.
        author = get_metadata_value(metadata, 'Artist')
        license_name = get_metadata_value(metadata, 'LicenseShortName')
        license_url = get_metadata_value(metadata, 'LicenseUrl')
        attribution = get_metadata_value(metadata, 'Attribution')

        # Используем уменьшенную версию изображения,
        # если Wikimedia предоставила её.
        image_url = (
            image_info.get('thumburl')
            or image_info.get('url')
        )

        if not image_url:
            continue

        images.append({
            'external_id': f"commons:{page['pageid']}",
            'title': page.get('title', ''),
            'image_url': image_url,
            'original_url': image_info.get('url', ''),
            'source_page': image_info.get('descriptionurl', ''),
            'author': author,
            'license_name': license_name,
            'license_url': license_url,
            'attribution': attribution,
        })

    return images
