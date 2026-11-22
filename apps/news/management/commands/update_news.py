
"""Команда для обновления новостей из RSS-источников."""

from django.core.management.base import BaseCommand, CommandError

from apps.news.models import NewsSource
from apps.news.services import update_news


class Command(BaseCommand):
    """Запускает обновление новостных источников."""

    help = 'Получить новости из активных RSS-источников'

    def add_arguments(self, parser):
        # Позволяет обновить только один источник по его ID
        parser.add_argument(
            '--source',
            type=int,
            help='Идентификатор конкретного RSS-источника',
        )

    def handle(self, *args, **options):
        source_id = options.get('source')

        # Проверяем указанный источник
        source = None

        if source_id is not None:
            try:
                source = NewsSource.objects.get(
                    source_id=source_id,
                    is_active=True,
                )
            except NewsSource.DoesNotExist:
                raise CommandError(
                    'Активный источник с таким идентификатором не найден.'
                )

        # Запускаем обновление новостей
        result = update_news(source)

        # Выводим статистику выполнения
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS('Обновление новостей завершено.')
        )

        self.stdout.write(
            f"Проверено источников: {result['sources_checked']}"
        )
        self.stdout.write(
            f"Найдено новостей: {result['items_found']}"
        )
        self.stdout.write(
            f"Добавлено новостей: {result['items_added']}"
        )
        self.stdout.write(
            f"Источников с ошибками: {result['sources_failed']}"
        )
