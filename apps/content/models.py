
from django.db import models


class ContentItem(models.Model):
    """Общая модель материалов базы знаний ITALIA ARCHIVE."""

    # Возможные типы материалов
    TYPE_CHOICES = [
        ('article', 'Статья'),
        ('image', 'Изображение'),
        ('video', 'Видео'),
        ('news', 'Новость'),
    ]

    # Возможные состояния публикации
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('published', 'Опубликован'),
        ('archived', 'В архиве'),
    ]

    # Уникальный идентификатор материала
    content_id = models.AutoField(primary_key=True)

    # Тип материала
    content_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES
    )

    # Название материала
    title = models.CharField(max_length=250)

    # Уникальный адрес страницы материала
    slug = models.SlugField(max_length=255, unique=True)

    # Краткое содержание материала
    summary = models.TextField()

    # Ссылка на оригинальную публикацию
    source_url = models.URLField(
        max_length=500,
        null=True,
        blank=True
    )

    # Название внешнего источника
    source_name = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )

    # Сведения о лицензии и условиях использования
    license_info = models.TextField(
        null=True,
        blank=True
    )

    # Показывать ли материал дополнительно в разделе статей
    show_in_articles = models.BooleanField(
        default=False,
        verbose_name='Показывать в разделе статей'
    )

    # Дата создания и последнего изменения записи
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Дата публикации материала
    published_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # Текущее состояние материала
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )

    class Meta:
        # Название таблицы в MySQL
        db_table = 'content_items'

    def __str__(self):
        return self.title


class Article(models.Model):
    """Полное содержимое статей базы знаний."""

    # Уникальный идентификатор статьи
    article_id = models.AutoField(primary_key=True)

    # Связь с общей записью материала
    content_item = models.OneToOneField(
        ContentItem,
        on_delete=models.CASCADE,
        related_name='article'
    )

    # Основной текст статьи
    body = models.TextField()

    # Автор или источник подготовки статьи
    author = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        # Название таблицы в MySQL
        db_table = 'articles'

    def __str__(self):
        return self.content_item.title


class Media(models.Model):
    """Изображения и видеоматериалы базы знаний."""

    # Уникальный идентификатор медиафайла
    media_id = models.AutoField(primary_key=True)

    # Связь с общей записью материала
    content_item = models.OneToOneField(
        ContentItem,
        on_delete=models.CASCADE,
        related_name='media'
    )

    # Тип медиафайла: изображение или видео
    MEDIA_TYPE_CHOICES = [
        ('image', 'Изображение'),
        ('video', 'Видео'),
    ]

    media_type = models.CharField(
        max_length=10,
        choices=MEDIA_TYPE_CHOICES
    )

    # Источник медиафайла
    MEDIA_SOURCE_CHOICES = [
        ('local', 'Локальный файл'),
        ('wikimedia', 'Wikimedia Commons'),
        ('youtube', 'YouTube'),
    ]

    media_source = models.CharField(
        max_length=20,
        choices=MEDIA_SOURCE_CHOICES,
        default='local',
        verbose_name='Источник материала'
    )

    # Уникальный идентификатор во внешнем источнике
    # Для уникальности будем добавлять префикс: commons: или youtube:
    external_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        verbose_name='Внешний идентификатор'
    )

    # Загруженный файл изображения
    image_file = models.ImageField(
        upload_to='images/',
        null=True,
        blank=True
    )

    # Внешняя ссылка на файл или видеоматериал
    file_url = models.URLField(
        max_length=500,
        null=True,
        blank=True
    )

    # Текстовое описание изображения для доступности
    alt_text = models.CharField(
        max_length=250,
        null=True,
        blank=True
    )

    # Дополнительная подпись к медиафайлу
    caption = models.CharField(
        max_length=500,
        null=True,
        blank=True
    )

    class Meta:
        # Название таблицы в MySQL
        db_table = 'media'

    def __str__(self):
        return f'{self.content_item.title} ({self.media_type})'


class Tag(models.Model):
    """Теги для классификации материалов и объектов."""

    # Уникальный идентификатор тега
    tag_id = models.AutoField(primary_key=True)

    # Название тега
    name = models.CharField(max_length=100, unique=True)

    # Уникальный адрес тега
    slug = models.SlugField(max_length=120, unique=True)

    # Описание назначения тега
    description = models.TextField(null=True, blank=True)

    class Meta:
        # Название таблицы в MySQL
        db_table = 'tags'

    def __str__(self):
        return self.name


class ContentItemTag(models.Model):
    """Связь материалов базы знаний с тегами."""

    # Уникальный идентификатор связи
    content_item_tag_id = models.AutoField(primary_key=True)

    # Материал, которому назначен тег
    content_item = models.ForeignKey(
        ContentItem,
        on_delete=models.CASCADE,
        related_name='tag_links'
    )

    # Тег, назначенный материалу
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='content_links'
    )

    class Meta:
        # Название промежуточной таблицы в MySQL
        db_table = 'content_item_tags'

        # Один тег нельзя дважды назначить одному материалу
        constraints = [
            models.UniqueConstraint(
                fields=['content_item', 'tag'],
                name='uq_content_item_tag'
            )
        ]

    def __str__(self):
        return f'{self.content_item.title} — {self.tag.name}'


class ObjectContentLink(models.Model):
    """Связь архитектурных объектов с информационными материалами."""

    # Уникальный идентификатор связи
    link_id = models.AutoField(primary_key=True)

    # Архитектурный объект, с которым связан материал
    architectural_object = models.ForeignKey(
        'catalog.ArchitecturalObject',
        on_delete=models.CASCADE,
        related_name='content_links'
    )

    # Статья, изображение, видео или другой материал
    content_item = models.ForeignKey(
        ContentItem,
        on_delete=models.CASCADE,
        related_name='object_links'
    )

    # Характер связи объекта с материалом
    LINK_TYPE_CHOICES = [
        ('describes', 'Описывает объект'),
        ('depicts', 'Изображает объект'),
        ('documents', 'Документирует объект'),
        ('related', 'Связанный материал'),
    ]

    link_type = models.CharField(
        max_length=20,
        choices=LINK_TYPE_CHOICES,
        default='related'
    )

    class Meta:
        db_table = 'object_content_links'

        # Один материал не должен повторно связываться с объектом
        constraints = [
            models.UniqueConstraint(
                fields=['architectural_object', 'content_item'],
                name='uq_object_content_link'
            )
        ]

    def __str__(self):
        return f'{self.architectural_object.name} — {self.content_item.title}'



class CityContentLink(models.Model):
    """Связь видеоматериалов с городами."""

    # Уникальный идентификатор связи
    city_content_link_id = models.AutoField(primary_key=True)

    # Город, к которому относится видео
    city = models.ForeignKey(
        'references.City',
        on_delete=models.PROTECT,
        related_name='video_links'
    )

    # Видеоматериал из общей таблицы материалов
    content_item = models.ForeignKey(
        ContentItem,
        on_delete=models.CASCADE,
        related_name='city_links'
    )

    class Meta:
        # Название таблицы в MySQL
        db_table = 'city_content_links'

        # Одно видео нельзя дважды связать с одним городом
        constraints = [
            models.UniqueConstraint(
                fields=['city', 'content_item'],
                name='uq_city_content_link'
            )
        ]

    def __str__(self):
        return f'{self.city.name} — {self.content_item.title}'
