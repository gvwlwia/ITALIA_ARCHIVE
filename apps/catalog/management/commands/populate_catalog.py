
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.catalog.models import (
    ArchitecturalObject,
    ObjectCity,
    ObjectStyle,
    ObjectEpoch,
    ObjectArchitect,
)
from apps.references.models import City, Style, Epoch, Architect


class Command(BaseCommand):
    help = "Заполнение каталога архитектурных объектов Италии"

    # Данные 20 архитектурных объектов.
    # Названия городов, стилей, эпох и архитекторов должны
    # соответствовать существующим записям справочников.
    objects = [
        {
            "name": "Колизей",
            "slug": "colosseum",
            "object_type": "Амфитеатр",
            "description": "Колизей — крупнейший амфитеатр Древнего Рима, расположенный в центре Рима. Сооружение использовалось для общественных зрелищ и стало одним из наиболее известных памятников античной архитектуры. Его конструкция сочетает арочные ярусы, систему сводов и развитую организацию зрительских мест.",
            "address": "Piazza del Colosseo, Roma",
            "year_start": 72,
            "year_end": 80,
            "date_note": "Строительство начато при Веспасиане и завершено при Тите.",
            "latitude": "41.8902100",
            "longitude": "12.4922310",
            "cities": [("Рим", "Лацио")],
            "styles": [("Древнеримский стиль", True)],
            "epochs": [("Античность", True)],
            "architects": [],
        },
        {
            "name": "Пантеон",
            "slug": "pantheon",
            "object_type": "Храм",
            "description": "Пантеон — древнеримский храм в Риме, известный своим монументальным куполом с центральным круглым отверстием — окулюсом. Здание демонстрирует высокий уровень развития римской инженерной и строительной техники.",
            "address": "Piazza della Rotonda, Roma",
            "year_start": 118,
            "year_end": 125,
            "date_note": "Современное здание возведено при императоре Адриане.",
            "latitude": "41.8986100",
            "longitude": "12.4768720",
            "cities": [("Рим", "Лацио")],
            "styles": [("Древнеримский стиль", True)],
            "epochs": [("Античность", True)],
            "architects": [("Аполлодор Дамасский", "Предполагаемый автор проекта; атрибуция не является бесспорной")],
        },
        {
            "name": "Форум Траяна",
            "slug": "forum-of-trajan",
            "object_type": "Архитектурный комплекс",
            "description": "Форум Траяна — один из крупнейших императорских форумов Рима. Комплекс включал площадь, базилику Ульпия, колонну Траяна и другие сооружения. Он отражает масштаб градостроительных и архитектурных проектов периода Римской империи.",
            "address": "Via dei Fori Imperiali, Roma",
            "year_start": 107,
            "year_end": 113,
            "date_note": "Основные сооружения комплекса были завершены в начале II века.",
            "latitude": "41.8955000",
            "longitude": "12.4843000",
            "cities": [("Рим", "Лацио")],
            "styles": [("Древнеримский стиль", True)],
            "epochs": [("Античность", True)],
            "architects": [("Аполлодор Дамасский", "Архитектор проекта")],
        },
        {
            "name": "Собор Санта-Мария-дель-Фьоре",
            "slug": "santa-maria-del-fiore",
            "object_type": "Собор",
            "description": "Собор Санта-Мария-дель-Фьоре — главный кафедральный собор Флоренции. Его архитектурный облик сочетает готическую основу и элементы эпохи Возрождения. Особую известность получил купол, спроектированный Филиппо Брунеллески.",
            "address": "Piazza del Duomo, Firenze",
            "year_start": 1296,
            "year_end": 1436,
            "date_note": "Строительство началось в XIII веке; купол Брунеллески завершён в XV веке.",
            "latitude": "43.7731000",
            "longitude": "11.2560000",
            "cities": [("Флоренция", "Тоскана")],
            "styles": [
                ("Готический стиль", True),
                ("Архитектура Возрождения", False),
            ],
            "epochs": [("Возрождение", True)],
            "architects": [
                ("Филиппо Брунеллески", "Автор проекта купола"),
            ],
        },
        {
            "name": "Пизанская башня",
            "slug": "leaning-tower-of-pisa",
            "object_type": "Колокольня",
            "description": "Пизанская башня — отдельно стоящая колокольня кафедрального комплекса Пизы. Она получила известность благодаря заметному наклону, возникшему в процессе строительства из-за особенностей грунта и основания сооружения.",
            "address": "Piazza del Duomo, Pisa",
            "year_start": 1173,
            "year_end": 1372,
            "date_note": "Строительство продолжалось с перерывами почти два столетия.",
            "latitude": "43.7230000",
            "longitude": "10.3966000",
            "cities": [("Пиза", "Тоскана")],
            "styles": [("Романский стиль", True)],
            "epochs": [("Романский период", True)],
            "architects": [],
        },
        {
            "name": "Дворец дожей",
            "slug": "doges-palace",
            "object_type": "Дворец",
            "description": "Дворец дожей — историческая резиденция правителей Венецианской республики. Здание является одним из наиболее известных памятников венецианской готики и отличается аркадными галереями и декоративным фасадом.",
            "address": "Piazza San Marco, Venezia",
            "year_start": 1340,
            "year_end": None,
            "date_note": "Основные строительные этапы относятся к XIV–XV векам.",
            "latitude": "45.4337000",
            "longitude": "12.3404000",
            "cities": [("Венеция", "Венето")],
            "styles": [("Готический стиль", True)],
            "epochs": [("Готика", True)],
            "architects": [],
        },
        {
            "name": "Собор Святого Петра",
            "slug": "st-peters-basilica",
            "object_type": "Базилика",
            "description": "Собор Святого Петра — крупнейший и один из наиболее значимых храмов Ватикана. Его современное здание создавалось несколькими поколениями архитекторов. Архитектурный облик включает элементы Высокого Возрождения и барокко.",
            "address": "Piazza San Pietro, Città del Vaticano",
            "year_start": 1506,
            "year_end": 1626,
            "date_note": "Строительство продолжалось более ста лет; освящение состоялось в 1626 году.",
            "latitude": "41.9022000",
            "longitude": "12.4539000",
            "cities": [("Ватикан", "Государство-город Ватикан")],
            "styles": [
                ("Архитектура Возрождения", True),
                ("Барокко", False),
            ],
            "epochs": [("Возрождение", True), ("Барокко", False)],
            "architects": [
                ("Донато Браманте", "Автор первоначального проекта"),
                ("Микеланджело Буонарроти", "Руководитель строительства и автор переработки проекта купола"),
                ("Карло Мадерно", "Автор проекта продольного нефа и фасада"),
                ("Джан Лоренцо Бернини", "Автор площади и колоннады"),
            ],
        },
        {
            "name": "Палаццо Питти",
            "slug": "palazzo-pitti",
            "object_type": "Дворец",
            "description": "Палаццо Питти — крупный дворцовый комплекс во Флоренции, расположенный на южном берегу реки Арно. Он представляет важный памятник архитектуры эпохи Возрождения и позднее неоднократно расширялся и перестраивался.",
            "address": "Piazza de' Pitti, Firenze",
            "year_start": 1458,
            "year_end": None,
            "date_note": "Строительство началось в XV веке; авторство первоначального проекта спорно.",
            "latitude": "43.7649000",
            "longitude": "11.2506000",
            "cities": [("Флоренция", "Тоскана")],
            "styles": [("Архитектура Возрождения", True)],
            "epochs": [("Возрождение", True)],
            "architects": [],
        },
        {
            "name": "Вилла Ротонда",
            "slug": "villa-rotonda",
            "object_type": "Вилла",
            "description": "Вилла Ротонда — загородная вилла архитектора Андреа Палладио, расположенная рядом с Виченцей. Здание известно симметричной композицией, центральным куполом и четырьмя портиками, обращёнными к разным сторонам света.",
            "address": "Via della Rotonda, Vicenza",
            "year_start": 1566,
            "year_end": 1591,
            "date_note": "Проектирование и строительство относятся ко второй половине XVI века.",
            "latitude": "45.5186000",
            "longitude": "11.5553000",
            "cities": [("Виченца", "Венето")],
            "styles": [("Архитектура Возрождения", True)],
            "epochs": [("Возрождение", True)],
            "architects": [("Андреа Палладио", "Автор проекта")],
        },
        {
            "name": "Базилика Сант-Андреа",
            "slug": "basilica-sant-andrea",
            "object_type": "Базилика",
            "description": "Базилика Сант-Андреа в Мантуе — один из наиболее значимых памятников архитектуры Возрождения. Проект Леона Баттисты Альберти отличается монументальным фасадом и использованием античных архитектурных мотивов.",
            "address": "Piazza Andrea Mantegna, Mantova",
            "year_start": 1472,
            "year_end": 1782,
            "date_note": "Проект создан Альберти; строительство и последующие работы продолжались несколько столетий.",
            "latitude": "45.1600000",
            "longitude": "10.7940000",
            "cities": [("Мантуя", "Ломбардия")],
            "styles": [("Архитектура Возрождения", True)],
            "epochs": [("Возрождение", True)],
            "architects": [("Леон Баттиста Альберти", "Автор первоначального проекта")],
        },
        {
            "name": "Собор Святого Марка",
            "slug": "st-marks-basilica",
            "object_type": "Базилика",
            "description": "Собор Святого Марка — главный храм Венеции, известный купольной композицией, мозаичным убранством и выраженным влиянием византийской архитектуры. Здание неоднократно перестраивалось и дополнялось.",
            "address": "Piazza San Marco, Venezia",
            "year_start": 1063,
            "year_end": 1094,
            "date_note": "Основной этап строительства современного здания относится к XI веку.",
            "latitude": "45.4345000",
            "longitude": "12.3397000",
            "cities": [("Венеция", "Венето")],
            "styles": [
                ("Византийская архитектура", True),
                ("Романский стиль", False),
            ],
            "epochs": [("Романский период", True)],
            "architects": [],
        },
        {
            "name": "Фонтан Треви",
            "slug": "trevi-fountain",
            "object_type": "Фонтан",
            "description": "Фонтан Треви — монументальный фонтан в Риме, созданный в стиле барокко. Архитектурная композиция объединяет скульптурные элементы и фасад дворца Поли, формируя единый городской ансамбль.",
            "address": "Piazza di Trevi, Roma",
            "year_start": 1732,
            "year_end": 1762,
            "date_note": "Основные работы проводились в XVIII веке; открытие состоялось в 1762 году.",
            "latitude": "41.9009000",
            "longitude": "12.4833000",
            "cities": [("Рим", "Лацио")],
            "styles": [("Барокко", True)],
            "epochs": [("Барокко", True)],
            "architects": [("Никола Сальви", "Автор проекта")],
        },
        {
            "name": "Базилика Суперга",
            "slug": "basilica-superga",
            "object_type": "Базилика",
            "description": "Базилика Суперга — монументальный храм на холме близ Турина. Проект Филиппо Ювары выполнен в духе позднего барокко и отличается центральным куполом и классическим портиком.",
            "address": "Strada Basilica di Superga, Torino",
            "year_start": 1717,
            "year_end": 1731,
            "date_note": "Строительство завершилось в первой половине XVIII века.",
            "latitude": "45.0772000",
            "longitude": "7.7685000",
            "cities": [("Турин", "Пьемонт")],
            "styles": [("Барокко", True)],
            "epochs": [("Барокко", True)],
            "architects": [("Филиппо Ювара", "Автор проекта")],
        },
        {
            "name": "Галерея Виктора Эммануила II",
            "slug": "galleria-vittorio-emanuele-ii",
            "object_type": "Торговая галерея",
            "description": "Галерея Виктора Эммануила II — историческая торговая галерея в центре Милана. Она известна стеклянной крышей, железными конструкциями, мозаичными полами и монументальной архитектурной композицией.",
            "address": "Piazza del Duomo, Milano",
            "year_start": 1865,
            "year_end": 1877,
            "date_note": "Открытие галереи состоялось в 1867 году; строительные работы завершались позднее.",
            "latitude": "45.4659000",
            "longitude": "9.1900000",
            "cities": [("Милан", "Ломбардия")],
            "styles": [("Эклектика (историзм)", True)],
            "epochs": [("XIX век", True)],
            "architects": [("Джузеппе Менгони", "Автор проекта")],
        },
        {
            "name": "Монументальное кладбище Милана",
            "slug": "monumental-cemetery-milan",
            "object_type": "Кладбищенский комплекс",
            "description": "Монументальное кладбище Милана — крупный архитектурно-мемориальный комплекс, известный разнообразием скульптурных и архитектурных памятников. Его оформление объединяет различные исторические стили и отражает развитие итальянской мемориальной архитектуры.",
            "address": "Piazzale Cimitero Monumentale, Milano",
            "year_start": 1863,
            "year_end": 1866,
            "date_note": "Открыто в 1866 году.",
            "latitude": "45.4859000",
            "longitude": "9.1730000",
            "cities": [("Милан", "Ломбардия")],
            "styles": [("Эклектика (историзм)", True)],
            "epochs": [("XIX век", True)],
            "architects": [("Карло Мачакини", "Автор проекта")],
        },
        {
            "name": "Центральный вокзал Милана",
            "slug": "milano-centrale",
            "object_type": "Железнодорожный вокзал",
            "description": "Центральный вокзал Милана — один из крупнейших железнодорожных вокзалов Италии. Его монументальная архитектура сочетает масштабные объёмы, декоративные элементы и инженерные конструкции.",
            "address": "Piazza Duca d'Aosta, Milano",
            "year_start": 1925,
            "year_end": 1931,
            "date_note": "Архитектурный конкурс состоялся в 1912 году; вокзал открыт в 1931 году.",
            "latitude": "45.4853000",
            "longitude": "9.2040000",
            "cities": [("Милан", "Ломбардия")],
            "styles": [("Эклектика (историзм)", True)],
            "epochs": [("XX век", True)],
            "architects": [("Улиссе Стаччини", "Автор архитектурного проекта")],
        },
        {
            "name": "Вилла Малапарте",
            "slug": "villa-malaparte",
            "object_type": "Вилла",
            "description": "Вилла Малапарте — частная вилла на острове Капри, расположенная на скалистом участке побережья. Здание известно выразительной геометрической формой, террасой-кровлей и тесной связью архитектуры с окружающим ландшафтом.",
            "address": "Punta Massullo, Capri",
            "year_start": 1938,
            "year_end": 1942,
            "date_note": "Авторство проекта является предметом дискуссий; Адальберто Либера рассматривается как предполагаемый автор первоначального проекта.",
            "latitude": "40.5480000",
            "longitude": "14.2460000",
            "cities": [("Капри", "Кампания")],
            "styles": [("Рационализм", True)],
            "epochs": [("XX век", True)],
            "architects": [
                ("Адальберто Либера", "Предполагаемый автор первоначального проекта"),
            ],
        },
        {
            "name": "Башня Пирелли",
            "slug": "pirelli-tower",
            "object_type": "Небоскрёб",
            "description": "Башня Пирелли — высотное офисное здание в Милане, ставшее важным примером послевоенной итальянской архитектуры. Проект сочетает архитектурную выразительность и инженерные решения железобетонного каркаса.",
            "address": "Piazza Duca d'Aosta, Milano",
            "year_start": 1956,
            "year_end": 1960,
            "date_note": "Здание завершено в 1960 году.",
            "latitude": "45.4855000",
            "longitude": "9.1990000",
            "cities": [("Милан", "Ломбардия")],
            "styles": [("Рационализм", True)],
            "epochs": [("XX век", True)],
            "architects": [
                ("Джо Понти", "Главный архитектор"),
                ("Пьер Луиджи Нерви", "Инженер-конструктор"),
            ],
        },
        {
            "name": "Национальный музей искусств XXI века (MAXXI)",
            "slug": "maxxi-museum",
            "object_type": "Музей",
            "description": "MAXXI — музей современного искусства и архитектуры в Риме. Здание, спроектированное Захой Хадид, отличается динамичной композицией, пересекающимися объёмами и сложной системой внутренних пространств.",
            "address": "Via Guido Reni, 4A, Roma",
            "year_start": 1998,
            "year_end": 2010,
            "date_note": "Музей открыт для посетителей в 2010 году.",
            "latitude": "41.9280000",
            "longitude": "12.4660000",
            "cities": [("Рим", "Лацио")],
            "styles": [("Современная архитектура", True)],
            "epochs": [("XXI век", True)],
            "architects": [("Заха Хадид", "Автор архитектурного проекта")],
        },
        {
            "name": "Аудиториум Парко-делла-Музика",
            "slug": "auditorium-parco-della-musica",
            "object_type": "Концертный комплекс",
            "description": "Аудиториум Парко-делла-Музика — многофункциональный концертный комплекс в Риме, включающий несколько залов и открытые пространства. Проект Ренцо Пиано объединяет современную архитектуру, акустику и общественную функцию.",
            "address": "Viale Pietro de Coubertin, Roma",
            "year_start": 1994,
            "year_end": 2002,
            "date_note": "Комплекс был открыт в 2002 году.",
            "latitude": "41.9290000",
            "longitude": "12.4750000",
            "cities": [("Рим", "Лацио")],
            "styles": [("Современная архитектура", True)],
            "epochs": [("XXI век", True)],
            "architects": [("Ренцо Пиано", "Автор архитектурного проекта")],
        },
    ]

    @transaction.atomic
    def handle(self, *args, **options):
        # Сначала проверяем, что все справочные записи существуют.
        errors = []

        for item in self.objects:
            for name, region in item["cities"]:
                if not City.objects.filter(name=name, region=region).exists():
                    errors.append(f"Город: {name} ({region})")

            for name, is_primary in item["styles"]:
                if not Style.objects.filter(name=name).exists():
                    errors.append(f"Стиль: {name}")

            for name, is_primary in item["epochs"]:
                if not Epoch.objects.filter(name=name).exists():
                    errors.append(f"Эпоха: {name}")

            for name, role in item["architects"]:
                if not Architect.objects.filter(full_name=name).exists():
                    errors.append(f"Архитектор: {name}")

        if errors:
            raise CommandError(
                "Не найдены необходимые справочные записи:\n"
                + "\n".join(errors)
            )

        # Заполняем архитектурные объекты и их связи.
        for item in self.objects:
            obj, created = ArchitecturalObject.objects.update_or_create(
                slug=item["slug"],
                defaults={
                    "name": item["name"],
                    "object_type": item["object_type"],
                    "description": item["description"],
                    "address": item["address"],
                    "year_start": item["year_start"],
                    "year_end": item["year_end"],
                    "date_note": item["date_note"],
                    "latitude": item["latitude"],
                    "longitude": item["longitude"],
                    "is_published": True,
                }
            )

            # Обновляем города объекта.
            city_ids = []
            for name, region in item["cities"]:
                city = City.objects.get(name=name, region=region)
                city_ids.append(city.pk)

                ObjectCity.objects.update_or_create(
                    architectural_object=obj,
                    city=city,
                    defaults={
                        "is_primary": True,
                    }
                )

            ObjectCity.objects.filter(
                architectural_object=obj
            ).exclude(city_id__in=city_ids).delete()

            # Обновляем стили объекта.
            style_ids = []
            for name, is_primary in item["styles"]:
                style = Style.objects.get(name=name)
                style_ids.append(style.pk)

                ObjectStyle.objects.update_or_create(
                    architectural_object=obj,
                    style=style,
                    defaults={
                        "is_primary": is_primary,
                    }
                )

            ObjectStyle.objects.filter(
                architectural_object=obj
            ).exclude(style_id__in=style_ids).delete()

            # Обновляем исторические эпохи объекта.
            epoch_ids = []
            for name, is_primary in item["epochs"]:
                epoch = Epoch.objects.get(name=name)
                epoch_ids.append(epoch.pk)

                ObjectEpoch.objects.update_or_create(
                    architectural_object=obj,
                    epoch=epoch,
                    defaults={
                        "is_primary": is_primary,
                    }
                )

            ObjectEpoch.objects.filter(
                architectural_object=obj
            ).exclude(epoch_id__in=epoch_ids).delete()

            # Обновляем архитекторов и их роли.
            architect_ids = []
            for name, role in item["architects"]:
                architect = Architect.objects.get(full_name=name)
                architect_ids.append(architect.pk)

                ObjectArchitect.objects.update_or_create(
                    architectural_object=obj,
                    architect=architect,
                    defaults={
                        "role": role,
                    }
                )

            ObjectArchitect.objects.filter(
                architectural_object=obj
            ).exclude(architect_id__in=architect_ids).delete()

            action = "Создан" if created else "Обновлён"
            self.stdout.write(f"{action}: {obj.name}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Каталог успешно заполнен. Всего объектов: "
                f"{ArchitecturalObject.objects.count()}"
            )
        )
