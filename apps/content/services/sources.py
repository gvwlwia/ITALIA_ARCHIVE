
"""Получение и обработка материалов из RSS- и Atom-источников."""

import re
import urllib.request
import xml.etree.ElementTree as ET

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime


# Максимальное время ожидания ответа источника
REQUEST_TIMEOUT = 20

# Название приложения при обращении к RSS-источникам
USER_AGENT = 'ITALIA ARCHIVE/1.0'


def parse_date(value):
    """Преобразует дату публикации в формат datetime."""

    if not value:
        return None

    # Пробуем обработать стандартный формат RSS
    try:
        result = parsedate_to_datetime(value)

        if result.tzinfo is None:
            result = result.replace(tzinfo=timezone.utc)

        return result

    except (TypeError, ValueError, OverflowError):
        pass

    # Пробуем обработать формат ISO 8601
    try:
        result = datetime.fromisoformat(
            value.replace('Z', '+00:00')
        )

        if result.tzinfo is None:
            result = result.replace(tzinfo=timezone.utc)

        return result

    except (TypeError, ValueError):
        return None


def get_element_text(element, names):
    """Находит текст элемента XML по названию тега."""

    for child in element.iter():
        name = child.tag.split('}')[-1].lower()

        if name in names and child.text:
            return child.text.strip()

    return ''


def repair_xml_ampersands(xml_data):
    """Исправляет незакодированные амперсанды в XML."""

    # Декодируем XML в текст
    xml_text = xml_data.decode('utf-8', errors='replace')

    # Заменяем амперсанды, которые не являются
    # частью XML-сущностей или числовых ссылок
    xml_text = re.sub(
        r'&(?!#\d+;|#x[0-9a-fA-F]+;|[a-zA-Z][a-zA-Z0-9]*;)',
        '&amp;',
        xml_text,
    )

    return xml_text.encode('utf-8')


def fetch_feed(feed_url):
    """Получает и разбирает RSS- или Atom-ленту."""

    # Формируем запрос к источнику
    request = urllib.request.Request(
        feed_url,
        headers={'User-Agent': USER_AGENT},
    )

    # Получаем XML от источника
    try:
        with urllib.request.urlopen(
            request,
            timeout=REQUEST_TIMEOUT,
        ) as response:
            xml_data = response.read()

    except Exception as error:
        raise RuntimeError(
            f'Не удалось получить данные из {feed_url}: {error}'
        ) from error

    # Сначала пробуем обычный разбор XML
    try:
        root = ET.fromstring(xml_data)

    except ET.ParseError:
        # Если XML содержит некорректные амперсанды,
        # исправляем их и повторяем разбор
        try:
            repaired_data = repair_xml_ampersands(xml_data)
            root = ET.fromstring(repaired_data)

        except (ET.ParseError, UnicodeError) as error:
            raise ValueError(
                f'Источник вернул некорректный XML: {feed_url}'
            ) from error

    # Определяем формат ленты
    root_name = root.tag.split('}')[-1].lower()

    if root_name == 'feed':
        # Формат Atom
        entries = [
            element
            for element in root
            if element.tag.split('}')[-1].lower() == 'entry'
        ]

    else:
        # Формат RSS
        entries = [
            element
            for element in root.iter()
            if element.tag.split('}')[-1].lower() == 'item'
        ]

    publications = []

    # Обрабатываем каждую публикацию
    for entry in entries:

        title = get_element_text(entry, {'title'})

        summary = get_element_text(
            entry,
            {'description', 'summary', 'content'},
        )

        # Получаем ссылку на публикацию
        link = ''

        for child in entry:
            if child.tag.split('}')[-1].lower() == 'link':

                # В Atom ссылка обычно находится в атрибуте href
                if child.attrib.get('rel', 'alternate') == 'alternate':
                    link = (
                        child.attrib.get('href')
                        or child.text
                        or ''
                    ).strip()

                if link:
                    break

        # Получаем идентификатор публикации
        external_id = get_element_text(entry, {'guid', 'id'})

        # Получаем дату публикации
        published_value = get_element_text(
            entry,
            {'pubdate', 'published', 'updated', 'date'},
        )

        # Получаем автора
        author = get_element_text(
            entry,
            {'author', 'creator'},
        )

        # Пропускаем публикации без названия или ссылки
        if not title or not link:
            continue

        publications.append({
            'title': title,
            'summary': summary,
            'original_url': link,
            'external_id': external_id or link,
            'author': author,
            'published_at': parse_date(published_value),
        })

    return publications
