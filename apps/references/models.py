
from django.db import models


class City(models.Model):
    """Справочник городов, в которых расположены архитектурные объекты."""

    # Уникальный идентификатор города
    city_id = models.AutoField(primary_key=True)

    # Название города и административный регион
    name = models.CharField(max_length=150)
    region = models.CharField(max_length=150)

    # Дополнительная информация о городе
    description = models.TextField(null=True, blank=True)

    # Географические координаты города
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

    class Meta:
        # Название таблицы в базе данных MySQL
        db_table = 'cities'

        # Один город не может повторяться в пределах одного региона
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'region'],
                name='uq_city_name_region'
            )
        ]

    def __str__(self):
        # Представление города в административной панели Django
        return f'{self.name}, {self.region}'



class Style(models.Model):
    """Справочник архитектурных стилей."""

    # Уникальный идентификатор стиля
    style_id = models.AutoField(primary_key=True)

    # Название архитектурного стиля
    name = models.CharField(max_length=150, unique=True)

    # Описание и временные границы существования стиля
    description = models.TextField(null=True, blank=True)
    period_start = models.SmallIntegerField(null=True, blank=True)
    period_end = models.SmallIntegerField(null=True, blank=True)

    # Родительский стиль для построения иерархии стилей
    parent_style = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_styles'
    )

    class Meta:
        # Название таблицы в базе данных
        db_table = 'styles'

    def __str__(self):
        return self.name


class Epoch(models.Model):
    """Справочник исторических эпох."""

    # Уникальный идентификатор эпохи
    epoch_id = models.AutoField(primary_key=True)

    # Название исторической эпохи
    name = models.CharField(max_length=150, unique=True)

    # Описание и временные границы эпохи
    description = models.TextField(null=True, blank=True)
    year_start = models.SmallIntegerField(null=True, blank=True)
    year_end = models.SmallIntegerField(null=True, blank=True)

    class Meta:
        # Название таблицы в базе данных
        db_table = 'epochs'

    def __str__(self):
        return self.name


class Architect(models.Model):
    """Справочник архитекторов, связанных с архитектурными объектами."""

    # Уникальный идентификатор архитектора
    architect_id = models.AutoField(primary_key=True)

    # Полное имя архитектора
    # Не устанавливаем unique=True: у разных людей могут совпадать имена
    full_name = models.CharField(max_length=200)

    # Годы рождения и смерти (могут быть неизвестны)
    birth_year = models.SmallIntegerField(null=True, blank=True)
    death_year = models.SmallIntegerField(null=True, blank=True)

    # Страна происхождения архитектора
    country = models.CharField(max_length=100, null=True, blank=True)

    # Биографическая информация
    biography = models.TextField(null=True, blank=True)

    # URL фотографии архитектора
    photo_url = models.URLField(max_length=500, null=True, blank=True)

    class Meta:
        # Название таблицы в базе данных
        db_table = 'architects'

    def __str__(self):
        return self.full_name
