from django.core.management.base import BaseCommand
from properties.models import (
    DealType, DealTypeTranslation,
    PropertyType, PropertyTypeTranslation,
    PropertyStatus, PropertyStatusTranslation,
    Attribute, AttributeTranslation,
    AttributePropertyType, AttributeChoice, AttributeChoiceTranslation,
    SiteSettings, Language,
)


class Command(BaseCommand):
    help = "Заполняет начальные справочники"

    def handle(self, *args, **kwargs):
        self.stdout.write("⏳ Заполняем справочники...")

        # ==============================================================
        # Типы сделок
        # ==============================================================
        sale, _ = DealType.objects.get_or_create(slug="sale", defaults={"sort_order": 1})
        DealTypeTranslation.objects.get_or_create(deal_type=sale, language=Language.RU, defaults={"title": "Продажа"})
        DealTypeTranslation.objects.get_or_create(deal_type=sale, language=Language.EN, defaults={"title": "Sale"})
        DealTypeTranslation.objects.get_or_create(deal_type=sale, language=Language.KA, defaults={"title": "გაყიდვა"})

        rent, _ = DealType.objects.get_or_create(slug="rent", defaults={"sort_order": 2})
        DealTypeTranslation.objects.get_or_create(deal_type=rent, language=Language.RU, defaults={"title": "Аренда"})
        DealTypeTranslation.objects.get_or_create(deal_type=rent, language=Language.EN, defaults={"title": "Rent"})
        DealTypeTranslation.objects.get_or_create(deal_type=rent, language=Language.KA, defaults={"title": "იჯარა"})

        self.stdout.write("✅ Типы сделок")

        # ==============================================================
        # Типы недвижимости
        # ==============================================================
        land, _ = PropertyType.objects.get_or_create(slug="land", defaults={"sort_order": 1})
        PropertyTypeTranslation.objects.get_or_create(property_type=land, language=Language.RU, defaults={"title": "Земельные участки"})
        PropertyTypeTranslation.objects.get_or_create(property_type=land, language=Language.EN, defaults={"title": "Land Plots"})
        PropertyTypeTranslation.objects.get_or_create(property_type=land, language=Language.KA, defaults={"title": "მიწის ნაკვეთები"})
        land.deal_types.add(sale)

        land_agri, _ = PropertyType.objects.get_or_create(slug="land-agricultural", defaults={"parent": land, "sort_order": 1})
        PropertyTypeTranslation.objects.get_or_create(property_type=land_agri, language=Language.RU, defaults={"title": "Сельскохозяйственного назначения"})
        PropertyTypeTranslation.objects.get_or_create(property_type=land_agri, language=Language.EN, defaults={"title": "Agricultural"})
        PropertyTypeTranslation.objects.get_or_create(property_type=land_agri, language=Language.KA, defaults={"title": "სასოფლო-სამეურნეო"})
        land_agri.deal_types.add(sale)

        land_non, _ = PropertyType.objects.get_or_create(slug="land-non-agricultural", defaults={"parent": land, "sort_order": 2})
        PropertyTypeTranslation.objects.get_or_create(property_type=land_non, language=Language.RU, defaults={"title": "Несельскохозяйственного назначения"})
        PropertyTypeTranslation.objects.get_or_create(property_type=land_non, language=Language.EN, defaults={"title": "Non-Agricultural"})
        PropertyTypeTranslation.objects.get_or_create(property_type=land_non, language=Language.KA, defaults={"title": "არასასოფლო-სამეურნეო"})
        land_non.deal_types.add(sale)

        apartment, _ = PropertyType.objects.get_or_create(slug="apartment", defaults={"sort_order": 2})
        PropertyTypeTranslation.objects.get_or_create(property_type=apartment, language=Language.RU, defaults={"title": "Квартиры"})
        PropertyTypeTranslation.objects.get_or_create(property_type=apartment, language=Language.EN, defaults={"title": "Apartments"})
        PropertyTypeTranslation.objects.get_or_create(property_type=apartment, language=Language.KA, defaults={"title": "ბინები"})
        apartment.deal_types.add(sale, rent)

        house, _ = PropertyType.objects.get_or_create(slug="house", defaults={"sort_order": 3})
        PropertyTypeTranslation.objects.get_or_create(property_type=house, language=Language.RU, defaults={"title": "Дома"})
        PropertyTypeTranslation.objects.get_or_create(property_type=house, language=Language.EN, defaults={"title": "Houses"})
        PropertyTypeTranslation.objects.get_or_create(property_type=house, language=Language.KA, defaults={"title": "სახლები"})
        house.deal_types.add(sale, rent)

        commercial, _ = PropertyType.objects.get_or_create(slug="commercial", defaults={"sort_order": 4})
        PropertyTypeTranslation.objects.get_or_create(property_type=commercial, language=Language.RU, defaults={"title": "Коммерция"})
        PropertyTypeTranslation.objects.get_or_create(property_type=commercial, language=Language.EN, defaults={"title": "Commercial"})
        PropertyTypeTranslation.objects.get_or_create(property_type=commercial, language=Language.KA, defaults={"title": "კომერციული"})
        commercial.deal_types.add(sale, rent)

        self.stdout.write("✅ Типы недвижимости")

        # ==============================================================
        # Статусы
        # ==============================================================
        statuses = [
            ("active",   "#27AE60", 1, "Активно",  "Active",  "აქტიური"),
            ("sold",     "#E74C3C", 2, "Продано",  "Sold",    "გაყიდული"),
            ("rented",   "#E74C3C", 3, "Сдано",    "Rented",  "გაქირავებული"),
            ("reserved", "#F39C12", 4, "Бронь",    "Reserved","დაჯავშნილი"),
            ("draft",    "#95A5A6", 5, "Черновик", "Draft",   "პროექტი"),
        ]
        for slug, color, order, ru, en, ka in statuses:
            st, _ = PropertyStatus.objects.get_or_create(slug=slug, defaults={"color": color, "sort_order": order})
            PropertyStatusTranslation.objects.get_or_create(status=st, language=Language.RU, defaults={"title": ru})
            PropertyStatusTranslation.objects.get_or_create(status=st, language=Language.EN, defaults={"title": en})
            PropertyStatusTranslation.objects.get_or_create(status=st, language=Language.KA, defaults={"title": ka})

        self.stdout.write("✅ Статусы")

        # ==============================================================
        # Характеристики
        # ==============================================================

        def make_attr(slug, value_type, unit, order, ru, en, ka, types):
            attr, _ = Attribute.objects.get_or_create(
                slug=slug,
                defaults={"value_type": value_type, "unit": unit, "sort_order": order}
            )
            AttributeTranslation.objects.get_or_create(attribute=attr, language=Language.RU, defaults={"title": ru})
            AttributeTranslation.objects.get_or_create(attribute=attr, language=Language.EN, defaults={"title": en})
            AttributeTranslation.objects.get_or_create(attribute=attr, language=Language.KA, defaults={"title": ka})
            for i, pt in enumerate(types):
                AttributePropertyType.objects.get_or_create(attribute=attr, property_type=pt, defaults={"sort_order": i})
            return attr

        rooms = make_attr("rooms", "integer", "комн.", 1, "Количество комнат", "Rooms", "ოთახების რაოდენობა", [apartment, house])
        floor = make_attr("floor", "integer", "эт.", 2, "Этаж", "Floor", "სართული", [apartment])
        floors_total = make_attr("floors_total", "integer", "эт.", 3, "Этажность дома", "Total Floors", "სართულების რაოდენობა", [apartment, house])
        area = make_attr("area", "decimal", "м²", 4, "Площадь", "Area", "ფართობი", [apartment, house, commercial, land, land_agri, land_non])
        balcony = make_attr("balcony", "boolean", "", 5, "Балкон", "Balcony", "აივანი", [apartment])

        self.stdout.write("✅ Базовые характеристики")

        # ==============================================================
        # Характеристика с вариантами — Тип коммерции
        # ==============================================================
        comm_type = make_attr("commercial_type", "choice", "", 6, "Тип коммерции", "Commercial Type", "კომერციული ტიპი", [commercial])

        for slug, ru, en, ka, order in [
            ("office",     "Офис",    "Office",    "ოფისი",    1),
            ("shop",       "Магазин", "Shop",      "მაღაზია",  2),
            ("warehouse",  "Склад",   "Warehouse", "საწყობი",  3),
            ("restaurant", "Ресторан","Restaurant","რესტორანი",4),
        ]:
            ch, _ = AttributeChoice.objects.get_or_create(attribute=comm_type, slug=slug, defaults={"sort_order": order})
            AttributeChoiceTranslation.objects.get_or_create(choice=ch, language=Language.RU, defaults={"title": ru})
            AttributeChoiceTranslation.objects.get_or_create(choice=ch, language=Language.EN, defaults={"title": en})
            AttributeChoiceTranslation.objects.get_or_create(choice=ch, language=Language.KA, defaults={"title": ka})

        self.stdout.write("✅ Типы коммерции")

        # ==============================================================
        # Настройки сайта
        # ==============================================================
        SiteSettings.objects.get_or_create(pk=1, defaults={
            "whatsapp_number": "",
            "phone_number": "",
            "email": "",
        })

        self.stdout.write("✅ Настройки сайта (заполните номер WhatsApp в админке)")
        self.stdout.write(self.style.SUCCESS("\n🎉 Все справочники заполнены успешно!"))