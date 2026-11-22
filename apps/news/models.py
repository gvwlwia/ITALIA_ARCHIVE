
from django.db import models


class NewsSource(models.Model):
    """Источники новостей, используемые для получения публикаций."""

    # Уникальный идентификатор источника
    source_id = models.AutoField(primary_key=True)

    # Название новостного источника
    name = models.CharField(max_length=200, unique=True)

    # Адрес официального сайта источника
    website_url = models.URLField(max_length=500, null=True, blank=True)

    # Адрес RSS-ленты или API для получения новостей
    feed_url = models.URLField(max_length=500)

    # Определяет, используется ли источник для обновления новостей
    is_active = models.BooleanField(default=True)

    # Дата и время последней проверки источника
    last_checked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'news_sources'

    def __str__(self):
        return self.name


class NewsItem(models.Model):
    """Специализированные сведения о новостях."""

    # Уникальный идентификатор новости
    news_id = models.AutoField(primary_key=True)

    # Связь с общей записью материала
    content_item = models.OneToOneField(
        'content.ContentItem',
        on_delete=models.CASCADE,
        related_name='news'
    )

    # Источник, из которого получена новость
    source = models.ForeignKey(
        NewsSource,
        on_delete=models.PROTECT,
        related_name='news_items'
    )

    # Оригинальная ссылка на новость на сайте источника
    original_url = models.URLField(max_length=700, unique=True)

    # Идентификатор публикации в исходной системе, если доступен
    external_id = models.CharField(
        max_length=250,
        null=True,
        blank=True
    )

    # Дата публикации новости в исходном источнике
    source_published_at = models.DateTimeField(null=True, blank=True)

    # Дата и время получения новости системой
    fetched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'news_items'

        # Идентификатор публикации не должен повторяться
        # в пределах одного источника, если он указан
        constraints = [
            models.UniqueConstraint(
                fields=['source', 'external_id'],
                name='uq_news_source_external_id'
            )
        ]

    def __str__(self):
        return self.content_item.title


class NewsUpdateLog(models.Model):
    """Журнал операций по обновлению новостной ленты."""

    # Возможные результаты выполнения обновления
    STATUS_CHOICES = [
        ('running', 'Выполняется'),
        ('success', 'Успешно'),
        ('failed', 'Ошибка'),
    ]

    # Уникальный идентификатор записи журнала
    log_id = models.AutoField(primary_key=True)

    # Источник, для которого выполнялось обновление.
    # Может отсутствовать при общем обновлении всех источников
    source = models.ForeignKey(
        NewsSource,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='update_logs'
    )

    # Дата и время начала обновления
    started_at = models.DateTimeField(auto_now_add=True)

    # Дата и время завершения обновления
    finished_at = models.DateTimeField(null=True, blank=True)

    # Результат выполнения операции
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='running'
    )

    # Количество найденных и добавленных новостей
    items_found = models.PositiveIntegerField(default=0)
    items_added = models.PositiveIntegerField(default=0)

    # Описание ошибки, если обновление завершилось неудачно
    error_message = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'news_update_logs'

    def __str__(self):
        return f'Обновление №{self.log_id} — {self.get_status_display()}'
