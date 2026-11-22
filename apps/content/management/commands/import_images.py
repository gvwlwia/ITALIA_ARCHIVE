
import re
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.content.models import ContentItem, Media, ObjectContentLink
from apps.catalog.models import ArchitecturalObject


class Command(BaseCommand):
    help = 'Импорт фотографий архитектурных объектов из папок'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            default='media/import_images',
            help='Папка с фотографиями для импорта'
        )

    def handle(self, *args, **options):
        source_dir = Path(options['source'])

        if not source_dir.exists():
            self.stdout.write(
                self.style.ERROR(f'Папка не найдена: {source_dir}')
            )
            return

        extensions = {'.jpg', '.jpeg', '.png', '.webp'}
        imported = 0
        skipped = 0

        # Каждая папка должна называться так же, как slug объекта
        for object_dir in source_dir.iterdir():
            if not object_dir.is_dir():
                continue

            architectural_object = ArchitecturalObject.objects.filter(
                slug=object_dir.name
            ).first()

            if not architectural_object:
                self.stdout.write(
                    self.style.WARNING(
                        f'Объект не найден: {object_dir.name}'
                    )
                )
                continue

            for image_path in object_dir.iterdir():
                if not image_path.is_file():
                    continue

                if image_path.suffix.lower() not in extensions:
                    continue

                # Создаём уникальный slug фотографии
                base_slug = slugify(
                    f'{object_dir.name}-{image_path.stem}'
                )

                content_item = ContentItem.objects.filter(
                    slug=base_slug
                ).first()

                # Если фотография уже импортирована, повторно её не добавляем
                if content_item:
                    skipped += 1
                    continue

                title = re.sub(
                    r'[_-]+', ' ', image_path.stem
                ).strip().title()

                content_item = ContentItem.objects.create(
                    content_type='image',
                    title=title,
                    slug=base_slug,
                    summary=f'Фотография объекта: {architectural_object.name}',
                    status='published'
                )

                # Сохраняем сам файл в MEDIA_ROOT/images/
                with image_path.open('rb') as image_file:
                    media = Media(
                        content_item=content_item,
                        media_type='image',
                        alt_text=title,
                        caption=title
                    )
                    media.image_file.save(
                        image_path.name,
                        image_file,
                        save=True
                    )

                # Связываем фотографию с архитектурным объектом
                ObjectContentLink.objects.get_or_create(
                    architectural_object=architectural_object,
                    content_item=content_item,
                    defaults={'link_type': 'depicts'}
                )

                imported += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Импорт завершён. Добавлено: {imported}, '
                f'пропущено: {skipped}.'
            )
        )
