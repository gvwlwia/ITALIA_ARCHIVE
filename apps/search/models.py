
from django.db import models


class SearchDocument(models.Model):
    """Поисковые документы для единого поиска по базе знаний."""

    # Уникальный идентификатор поискового документа
    document_id = models.AutoField(primary_key=True)

    # Тип сущности, к которой относится поисковый документ
    ENTITY_TYPE_CHOICES = [
        ('object', 'Архитектурный объект'),
        ('article', 'Статья'),
        ('image', 'Изображение'),
        ('video', 'Видео'),
        ('news', 'Новость'),
        ('city', 'Город'),
        ('style', 'Архитектурный стиль'),
        ('epoch', 'Историческая эпоха'),
        ('architect', 'Архитектор'),
        ('tag', 'Тег'),
    ]

    entity_type = models.CharField(
        max_length=20,
        choices=ENTITY_TYPE_CHOICES
    )

    # Идентификатор исходной записи в соответствующей таблице.
    # Внешний ключ не используется, так как запись может относиться
    # к разным таблицам базы данных
    entity_id = models.PositiveIntegerField()

    # Название сущности, отображаемое в результатах поиска
    title = models.CharField(max_length=250)

    # Подготовленный текст для поиска:
    # описания, ключевые слова, теги и другие значимые сведения
    search_text = models.TextField()

    # Дата и время последнего обновления поискового документа
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'search_documents'

        # Для одной исходной записи создаётся только один
        # поисковый документ соответствующего типа
        constraints = [
            models.UniqueConstraint(
                fields=['entity_type', 'entity_id'],
                name='uq_search_entity'
            )
        ]

    def __str__(self):
        return f'{self.title} ({self.get_entity_type_display()})'
