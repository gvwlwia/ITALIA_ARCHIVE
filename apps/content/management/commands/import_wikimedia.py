
"""Импорт фотографий из Wikimedia Commons в ITALIA ARCHIVE."""

from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from apps.catalog.models import ArchitecturalObject
from apps.content.models import ContentItem, Media, ObjectContentLink

from apps.content.services.wikimedia import fetch_commons_images


class Command(BaseCommand):
    help = 'Импорт фотографий архитектурных объектов из Wikimedia Commons'

    def add_arguments(self, parser):
        # Название архитектурного объекта для поиска фотографий.
        parser.add_argument(
            '--object',
            required=True,
            help='Название архитектурного объекта в базе данных',
        )

        # Поисковая фраза для Wikimedia Commons.
        parser.add_argument(
            '--query',
            required=True,
            help='Поисковый запрос для Wikimedia Commons',
        )

        # Максимальное количество фотографий.
        parser.add_argument(
            '--limit',
            type=int,
            default=5,
            help='Количество фотографий для поиска (по умолчанию 5)',
        )

    def handle(self, *args, **options):
        object_name = options['object']
        search_query = options['query']
        limit = options['limit']

        if limit < 1 or limit > 50:
            raise CommandError('Количество фотографий должно быть от 1 до 50.')

        # Находим архитектурный объект в собственной базе.
        architectural_object = (
            ArchitecturalObject.objects
            .filter(name__iexact=object_name)
            .first()
        )

        if not architectural_object:
            raise CommandError(
                f'Архитектурный объект «{object_name}» не найден.'
            )

        self.stdout.write(
            self.style.NOTICE(
                f'Поиск фотографий для объекта: {architectural_object.name}'
            )
        )

        # Получаем фотографии из Wikimedia Commons.
        try:
            images = fetch_commons_images(
                search_query,
                limit=limit,
            )
        except Exception as error:
            raise CommandError(str(error)) from error

        if not images:
            self.stdout.write(
                self.style.WARNING('Фотографии не найдены.')
            )
            return

        imported_count = 0
        skipped_count = 0

        for image in images:
            external_id = image['external_id']

            # Проверяем, не импортировалась ли фотография ранее.
            if Media.objects.filter(external_id=external_id).exists():
                self.stdout.write(
                    f'Пропуск: {image["title"]} — уже импортирована.'
                )
                skipped_count += 1
                continue

            # Формируем название материала.
            title = image['title'].replace('File:', '').strip()

            # Сохраняем сведения об авторстве и лицензии.
            author = image.get('author', '')
            license_name = image.get('license_name', '')
            license_url = image.get('license_url', '')
            attribution = image.get('attribution', '')

            summary_parts = []

            if author:
                summary_parts.append(f'Автор: {author}')

            if attribution:
                summary_parts.append(f'Атрибуция: {attribution}')

            if license_name:
                summary_parts.append(f'Лицензия: {license_name}')

            if license_url:
                summary_parts.append(f'Ссылка на лицензию: {license_url}')

            summary = '\n'.join(summary_parts)

            # Создаём запись общего типа контента.
            content_item = ContentItem.objects.create(
                content_type='image',
                title=title,
                slug=slugify(
                    f'{architectural_object.slug}-{external_id}'
                )[:255],
                summary=summary,
                source_url=image.get('source_page', ''),
                source_name='Wikimedia Commons',
                license_info=license_name,
                status='draft',
                show_in_articles=False,
            )

            # Создаём запись изображения.
            Media.objects.create(
                content_item=content_item,
                media_type='image',
                media_source='wikimedia',
                external_id=external_id,
                file_url=image['image_url'],
                alt_text=title,
                caption=summary,
            )

            # Связываем фотографию с архитектурным объектом.
            ObjectContentLink.objects.create(
                architectural_object=architectural_object,
                content_item=content_item,
                link_type='depicts',
            )

            imported_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f'Добавлена фотография: {title}'
                )
            )

        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(
                f'Импорт завершён. Добавлено: {imported_count}; '
                f'пропущено: {skipped_count}.'
            )
        )
        self.stdout.write(
            self.style.WARNING(
                'Новые фотографии сохранены как черновики. '
                'Перед публикацией проверь их в админ-панели.'
            )
        )
