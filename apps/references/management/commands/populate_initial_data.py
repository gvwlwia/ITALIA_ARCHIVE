
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.references.models import City, Style, Epoch, Architect


class Command(BaseCommand):
    help = "Заполнение и обновление начальных справочных данных"

    @transaction.atomic
    def handle(self, *args, **options):

        # Города и регионы Италии
        cities = [
            ("Рим", "Лацио"),
            ("Флоренция", "Тоскана"),
            ("Венеция", "Венето"),
            ("Милан", "Ломбардия"),
            ("Неаполь", "Кампания"),
            ("Пиза", "Тоскана"),
            ("Верона", "Венето"),
            ("Сиена", "Тоскана"),
            ("Турин", "Пьемонт"),
            ("Болонья", "Эмилия-Романья"),
            ("Виченца", "Венето"),
            ("Мантуя", "Ломбардия"),
            ("Капри", "Кампания"),
            ("Ватикан", "Государство-город Ватикан"),
        ]

        for name, region in cities:
            City.objects.get_or_create(
                name=name,
                region=region
            )

        # Приводим некоторые старые названия стилей к единому формату
        style_renames = {
            "Древнеримская архитектура": "Древнеримский стиль",
            "Готика": "Готический стиль",
        }

        for old_name, new_name in style_renames.items():
            old_style = Style.objects.filter(name=old_name).first()

            if old_style and not Style.objects.filter(name=new_name).exists():
                old_style.name = new_name
                old_style.save(update_fields=["name"])

        # Архитектурные стили
        styles = [
            "Древнеримский стиль",
            "Византийская архитектура",
            "Романский стиль",
            "Готический стиль",
            "Архитектура Возрождения",
            "Маньеризм",
            "Барокко",
            "Рококо",
            "Неоклассицизм",
            "Модерн",
            "Рационализм",
            "Эклектика (историзм)",
            "Современная архитектура",
        ]

        for name in styles:
            Style.objects.get_or_create(name=name)

        # Обновляем названия существующих исторических эпох
        epoch_renames = {
            "Древний Рим": "Античность",
            "Готический период": "Готика",
            "Новое время": "Барокко",
            "Современность": "XXI век",
        }

        for old_name, new_name in epoch_renames.items():
            old_epoch = Epoch.objects.filter(name=old_name).first()

            if old_epoch and not Epoch.objects.filter(name=new_name).exists():
                old_epoch.name = new_name
                old_epoch.save(update_fields=["name"])

        # Исторические эпохи
        epochs = [
            "Античность",
            "Раннее Средневековье",
            "Романский период",
            "Готика",
            "Возрождение",
            "Барокко",
            "XIX век",
            "XX век",
            "XXI век",
        ]

        for name in epochs:
            Epoch.objects.get_or_create(name=name)

        # Архитекторы, необходимые для каталога
        architects = [
            "Витрувий",
            "Филиппо Брунеллески",
            "Леон Баттиста Альберти",
            "Донато Браманте",
            "Микеланджело Буонарроти",
            "Андреа Палладио",
            "Джан Лоренцо Бернини",
            "Франческо Борромини",
            "Джузеппе Пьермарини",
            "Ренцо Пиано",
            "Аполлодор Дамасский",
            "Никола Сальви",
            "Филиппо Ювара",
            "Джузеппе Менгони",
            "Улиссе Стаччини",
            "Джо Понти",
            "Пьер Луиджи Нерви",
            "Заха Хадид",
            "Карло Мачакини",
            "Адальберто Либера",
            "Карло Мадерно",
        ]

        for full_name in architects:
            Architect.objects.get_or_create(full_name=full_name)

        self.stdout.write(
            self.style.SUCCESS(
                "Справочные данные успешно обновлены!"
            )
        )

        self.stdout.write(f"Городов: {City.objects.count()}")
        self.stdout.write(f"Стилей: {Style.objects.count()}")
        self.stdout.write(f"Эпох: {Epoch.objects.count()}")
        self.stdout.write(f"Архитекторов: {Architect.objects.count()}")
