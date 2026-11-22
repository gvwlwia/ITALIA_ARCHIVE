
from django.db import models


class ArchitecturalObject(models.Model):
    """Архитектурный объект Италии."""

    # Уникальный идентификатор архитектурного объекта
    object_id = models.AutoField(primary_key=True)

    # Основная информация об объекте
    name = models.CharField(max_length=250)

    # Уникальный адрес страницы объекта в веб-приложении
    slug = models.SlugField(max_length=255, unique=True)

    # Тип объекта: храм, дворец, мост, вилла и т. д.
    object_type = models.CharField(max_length=100)

    # Подробное описание архитектурного объекта
    description = models.TextField()

    # Физический адрес объекта
    address = models.CharField(max_length=250, null=True, blank=True)

    # Временные границы строительства или создания объекта
    year_start = models.SmallIntegerField(null=True, blank=True)
    year_end = models.SmallIntegerField(null=True, blank=True)

    # Дополнительное пояснение к датировке объекта
    date_note = models.CharField(max_length=250, null=True, blank=True)

    # Географические координаты архитектурного объекта
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )

    # Дата и время создания и последнего изменения записи
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Определяет, доступен ли объект посетителям сайта
    is_published = models.BooleanField(default=False)

    class Meta:
        # Название таблицы в базе данных MySQL
        db_table = 'architectural_objects'

    def __str__(self):
        # Отображение названия объекта в административной панели
        return self.name

class ObjectCity(models.Model):
    """Связь архитектурных объектов с городами."""

    # Уникальный идентификатор связи
    object_city_id = models.AutoField(primary_key=True)

    # Архитектурный объект, к которому относится город
    architectural_object = models.ForeignKey(
        ArchitecturalObject,
        on_delete=models.CASCADE,
        related_name='city_links'
    )

    # Город, связанный с архитектурным объектом
    city = models.ForeignKey(
        'references.City',
        on_delete=models.PROTECT,
        related_name='object_links'
    )

    # Признак основного города для данного объекта
    is_primary = models.BooleanField(default=False)

    class Meta:
        # Название промежуточной таблицы в MySQL
        db_table = 'object_cities'

        # Один и тот же город нельзя дважды связать с одним объектом
        constraints = [
            models.UniqueConstraint(
                fields=['architectural_object', 'city'],
                name='uq_object_city'
            )
        ]

    def __str__(self):
        # Представление связи в административной панели
        return f'{self.architectural_object.name} — {self.city.name}'

class ObjectStyle(models.Model):
    """Связь архитектурных объектов с архитектурными стилями."""

    # Уникальный идентификатор связи
    object_style_id = models.AutoField(primary_key=True)

    # Архитектурный объект
    architectural_object = models.ForeignKey(
        ArchitecturalObject,
        on_delete=models.CASCADE,
        related_name='style_links'
    )

    # Архитектурный стиль из справочника
    style = models.ForeignKey(
        'references.Style',
        on_delete=models.PROTECT,
        related_name='object_links'
    )

    # Признак основного архитектурного стиля объекта
    is_primary = models.BooleanField(default=False)

    class Meta:
        # Название промежуточной таблицы в MySQL
        db_table = 'object_styles'

        # Исключаем повторение одной пары «объект — стиль»
        constraints = [
            models.UniqueConstraint(
                fields=['architectural_object', 'style'],
                name='uq_object_style'
            )
        ]

    def __str__(self):
        # Представление связи в административной панели
        return f'{self.architectural_object.name} — {self.style.name}'


class ObjectEpoch(models.Model):
    """Связь архитектурных объектов с историческими эпохами."""

    # Уникальный идентификатор связи
    object_epoch_id = models.AutoField(primary_key=True)

    # Архитектурный объект
    architectural_object = models.ForeignKey(
        ArchitecturalObject,
        on_delete=models.CASCADE,
        related_name='epoch_links'
    )

    # Историческая эпоха из справочника
    epoch = models.ForeignKey(
        'references.Epoch',
        on_delete=models.PROTECT,
        related_name='object_links'
    )

    # Признак основной исторической эпохи объекта
    is_primary = models.BooleanField(default=False)

    class Meta:
        # Название промежуточной таблицы в MySQL
        db_table = 'object_epochs'

        # Исключаем повторение одной пары «объект — эпоха»
        constraints = [
            models.UniqueConstraint(
                fields=['architectural_object', 'epoch'],
                name='uq_object_epoch'
            )
        ]

    def __str__(self):
        # Представление связи в административной панели
        return f'{self.architectural_object.name} — {self.epoch.name}'



class ObjectArchitect(models.Model):
    """Связь архитектурных объектов с архитекторами."""

    # Уникальный идентификатор связи
    object_architect_id = models.AutoField(primary_key=True)

    # Архитектурный объект
    architectural_object = models.ForeignKey(
        ArchitecturalObject,
        on_delete=models.CASCADE,
        related_name='architect_links'
    )

    # Архитектор из справочника
    architect = models.ForeignKey(
        'references.Architect',
        on_delete=models.PROTECT,
        related_name='object_links'
    )

    # Роль архитектора в создании объекта
    role = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    class Meta:
        # Название промежуточной таблицы в MySQL
        db_table = 'object_architects'

        # Исключаем повторение одной пары «объект — архитектор»
        constraints = [
            models.UniqueConstraint(
                fields=['architectural_object', 'architect'],
                name='uq_object_architect'
            )
        ]

    def __str__(self):
        # Представление связи в административной панели
        return f'{self.architectural_object.name} — {self.architect.full_name}'


class ObjectTag(models.Model):
    """Связь архитектурных объектов с тематическими тегами."""

    # Уникальный идентификатор связи
    object_tag_id = models.AutoField(primary_key=True)

    # Архитектурный объект, которому назначен тег
    architectural_object = models.ForeignKey(
        ArchitecturalObject,
        on_delete=models.CASCADE,
        related_name='tag_links'
    )

    # Тег, назначенный архитектурному объекту
    tag = models.ForeignKey(
        'content.Tag',
        on_delete=models.CASCADE,
        related_name='object_links'
    )

    class Meta:
        db_table = 'object_tags'

        # Один и тот же тег нельзя назначить объекту повторно
        constraints = [
            models.UniqueConstraint(
                fields=['architectural_object', 'tag'],
                name='uq_object_tag'
            )
        ]

    def __str__(self):
        return f'{self.architectural_object.name} — {self.tag.name}'
