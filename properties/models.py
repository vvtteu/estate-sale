from django.conf import settings
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _


class Language(models.TextChoices):
    RU = "ru", _("Русский")
    EN = "en", _("English")
    KA = "ka", _("ქართული")


class BaseModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Создано")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Обновлено")
    )

    class Meta:
        abstract = True


class TranslationBase(BaseModel):
    language = models.CharField(
        max_length=2,
        choices=Language.choices,
        db_index=True,
        verbose_name=_("Язык")
    )

    class Meta:
        abstract = True


# ==============================================================================
# Тип сделки (Продажа / Аренда)
# ==============================================================================

class DealType(BaseModel):
    slug = models.SlugField(
        unique=True,
        verbose_name=_("Slug"),
        help_text=_("Используется в URL. Только латинские буквы и дефис.")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Активно")
    )
    sort_order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("Порядок сортировки")
    )

    class Meta:
        ordering = ("sort_order",)
        verbose_name = _("Тип сделки")
        verbose_name_plural = _("Типы сделок")

    def __str__(self):
        translation = self.translations.filter(language=Language.RU).first()
        return translation.title if translation else self.slug


class DealTypeTranslation(TranslationBase):
    deal_type = models.ForeignKey(
        DealType,
        related_name="translations",
        on_delete=models.CASCADE,
        verbose_name=_("Тип сделки")
    )
    title = models.CharField(
        max_length=100,
        verbose_name=_("Название")
    )

    class Meta:
        unique_together = ("deal_type", "language")
        verbose_name = _("Перевод типа сделки")
        verbose_name_plural = _("Переводы типов сделок")

    def __str__(self):
        return self.title


# ==============================================================================
# Тип недвижимости — дерево
# ==============================================================================

class PropertyType(BaseModel):
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE,
        verbose_name=_("Родительская категория"),
        help_text=_("Оставьте пустым для категории верхнего уровня.")
    )
    slug = models.SlugField(
        unique=True,
        verbose_name=_("Slug")
    )
    icon = models.ImageField(
        upload_to="property_types/",
        blank=True,
        null=True,
        verbose_name=_("Иконка")
    )
    deal_types = models.ManyToManyField(
        DealType,
        related_name="property_types",
        blank=True,
        verbose_name=_("Применимые типы сделок"),
        help_text=_("К каким типам сделок относится данная категория.")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Активно")
    )
    sort_order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("Порядок сортировки")
    )

    class Meta:
        ordering = ("sort_order",)
        verbose_name = _("Тип недвижимости")
        verbose_name_plural = _("Типы недвижимости")

    def __str__(self):
        translation = self.translations.filter(language=Language.RU).first()
        return translation.title if translation else self.slug


class PropertyTypeTranslation(TranslationBase):
    property_type = models.ForeignKey(
        PropertyType,
        related_name="translations",
        on_delete=models.CASCADE,
        verbose_name=_("Тип недвижимости")
    )
    title = models.CharField(
        max_length=150,
        verbose_name=_("Название")
    )

    class Meta:
        unique_together = ("property_type", "language")
        verbose_name = _("Перевод типа недвижимости")
        verbose_name_plural = _("Переводы типов недвижимости")

    def __str__(self):
        return self.title


# ==============================================================================
# Статус объявления
# ==============================================================================

class PropertyStatus(BaseModel):
    slug = models.SlugField(
        unique=True,
        verbose_name=_("Slug"),
        help_text=_("Например: active, sold, rented, reserved, draft")
    )
    color = models.CharField(
        max_length=7,
        blank=True,
        verbose_name=_("Цвет (HEX)"),
        help_text=_("Цвет бэйджика на карточке. Например: #27AE60")
    )
    sort_order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("Порядок сортировки")
    )

    class Meta:
        ordering = ("sort_order",)
        verbose_name = _("Статус объявления")
        verbose_name_plural = _("Статусы объявлений")

    def __str__(self):
        translation = self.translations.filter(language=Language.RU).first()
        return translation.title if translation else self.slug


class PropertyStatusTranslation(TranslationBase):
    status = models.ForeignKey(
        PropertyStatus,
        related_name="translations",
        on_delete=models.CASCADE,
        verbose_name=_("Статус")
    )
    title = models.CharField(
        max_length=100,
        verbose_name=_("Название")
    )

    class Meta:
        unique_together = ("status", "language")
        verbose_name = _("Перевод статуса")
        verbose_name_plural = _("Переводы статусов")

    def __str__(self):
        return self.title


# ==============================================================================
# Валюта / Курс
# ==============================================================================

class Currency(models.TextChoices):
    USD = "USD", "USD"
    GEL = "GEL", "GEL"


class ExchangeRate(BaseModel):
    usd_to_gel = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        verbose_name=_("Курс USD → GEL"),
        help_text=_("Сколько лари за 1 доллар. Например: 2.6500")
    )
    effective_date = models.DateField(
        unique=True,
        verbose_name=_("Дата")
    )

    class Meta:
        ordering = ("-effective_date",)
        verbose_name = _("Курс валют")
        verbose_name_plural = _("Курсы валют")

    def __str__(self):
        return f"1 USD = {self.usd_to_gel} GEL ({self.effective_date})"


# ==============================================================================
# Объект недвижимости
# ==============================================================================

class Property(BaseModel):
    deal_type = models.ForeignKey(
        DealType,
        related_name="properties",
        on_delete=models.PROTECT,
        verbose_name=_("Тип сделки")
    )
    property_type = models.ForeignKey(
        PropertyType,
        related_name="properties",
        on_delete=models.PROTECT,
        verbose_name=_("Тип недвижимости")
    )
    status = models.ForeignKey(
        PropertyStatus,
        related_name="properties",
        on_delete=models.PROTECT,
        verbose_name=_("Статус")
    )

    city = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name=_("Город"),
        help_text=_("Например: Тбилиси")
    )
    district = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name=_("Район"),
        help_text=_("Например: Ваке")
    )

    price = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        db_index=True,
        verbose_name=_("Цена"),
        help_text=_("Введите цену в выбранной валюте.")
    )
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.GEL,
        verbose_name=_("Валюта")
    )

    location = models.PointField(
        geography=True,
        srid=4326,
        null=True,
        blank=True,
        verbose_name=_("Местоположение на карте"),
        help_text=_("Кликните на карте, чтобы указать точное местоположение объекта.")
    )

    address = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_("Адрес"),
        help_text=_("Заполняется автоматически при клике на карте, можно поправить вручную.")
    )
    
    area_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Общая площадь, м²")
    )
    slug = models.SlugField(
        unique=True,
        max_length=255,
        verbose_name=_("Slug"),
        help_text=_("Уникальный идентификатор для URL. Заполняется вручную латиницей.")
    )
    is_published = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_("Опубликовано"),
        help_text=_("Снимите галочку, чтобы скрыть объявление с сайта.")
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Дата публикации")
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_properties",
        verbose_name=_("Создал")
    )

    class Meta:
        indexes = [
            models.Index(fields=["deal_type", "property_type", "status"]),
        ]
        verbose_name = _("Объект недвижимости")
        verbose_name_plural = _("Объекты недвижимости")

    def __str__(self):
        translation = self.translations.filter(language=Language.RU).first()
        return translation.title if translation else self.slug


class PropertyTranslation(TranslationBase):
    property = models.ForeignKey(
        Property,
        related_name="translations",
        on_delete=models.CASCADE,
        verbose_name=_("Объект")
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_("Заголовок"),
        help_text=_("Например: 3-комнатная квартира в центре Тбилиси")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Описание")
    )
    address_text = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_("Адрес (текст)"),
        help_text=_("Например: ул. Руставели 5, кв. 12. Отображается на карточке.")
    )

    class Meta:
        unique_together = ("property", "language")
        verbose_name = _("Перевод объекта")
        verbose_name_plural = _("Переводы объектов")

    def __str__(self):
        return self.title


# ==============================================================================
# Фото
# ==============================================================================

class PropertyImage(BaseModel):
    property = models.ForeignKey(
        Property,
        related_name="images",
        on_delete=models.CASCADE,
        verbose_name=_("Объект")
    )
    image = models.ImageField(
        upload_to="properties/%Y/%m/",
        verbose_name=_("Фотография")
    )
    is_main = models.BooleanField(
        default=False,
        verbose_name=_("Главное фото"),
        help_text=_("Отображается на превью карточки.")
    )
    sort_order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("Порядок")
    )
    alt_text = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Описание фото"),
        help_text=_("Для SEO. Например: вид из окна на горы.")
    )

    class Meta:
        ordering = ("sort_order",)
        verbose_name = _("Фотография")
        verbose_name_plural = _("Фотографии")

    def __str__(self):
        return f"Фото #{self.sort_order} — {self.property}"


# ==============================================================================
# Динамические характеристики
# ==============================================================================

class AttributeValueType(models.TextChoices):
    INTEGER = "integer", _("Целое число")
    DECIMAL = "decimal", _("Десятичное число")
    BOOLEAN = "boolean", _("Да / Нет")
    TEXT    = "text",    _("Текст")
    CHOICE  = "choice",  _("Вариант выбора")


class Attribute(BaseModel):
    slug = models.SlugField(
        unique=True,
        verbose_name=_("Slug"),
        help_text=_("Например: rooms, floor, balcony")
    )
    value_type = models.CharField(
        max_length=10,
        choices=AttributeValueType.choices,
        verbose_name=_("Тип значения"),
        help_text=_("Определяет, какое поле будет заполнять администратор.")
    )
    unit = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Единица измерения"),
        help_text=_("Например: м², эт., км. Отображается рядом со значением.")
    )
    is_filterable = models.BooleanField(
        default=True,
        verbose_name=_("Участвует в фильтрации"),
        help_text=_("Если включено — характеристика доступна в фильтрах на сайте.")
    )
    sort_order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("Порядок сортировки")
    )
    property_types = models.ManyToManyField(
        PropertyType,
        related_name="attributes",
        through="AttributePropertyType",
        verbose_name=_("Типы недвижимости")
    )

    class Meta:
        ordering = ("sort_order",)
        verbose_name = _("Характеристика")
        verbose_name_plural = _("Характеристики")

    def __str__(self):
        translation = self.translations.filter(language=Language.RU).first()
        return translation.title if translation else self.slug


class AttributeTranslation(TranslationBase):
    attribute = models.ForeignKey(
        Attribute,
        related_name="translations",
        on_delete=models.CASCADE,
        verbose_name=_("Характеристика")
    )
    title = models.CharField(
        max_length=150,
        verbose_name=_("Название")
    )

    class Meta:
        unique_together = ("attribute", "language")
        verbose_name = _("Перевод характеристики")
        verbose_name_plural = _("Переводы характеристик")

    def __str__(self):
        return self.title


class AttributePropertyType(BaseModel):
    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE,
        verbose_name=_("Характеристика")
    )
    property_type = models.ForeignKey(
        PropertyType,
        on_delete=models.CASCADE,
        verbose_name=_("Тип недвижимости")
    )
    is_required = models.BooleanField(
        default=False,
        verbose_name=_("Обязательна для заполнения")
    )
    sort_order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("Порядок")
    )

    class Meta:
        unique_together = ("attribute", "property_type")
        verbose_name = _("Связь характеристики с типом")
        verbose_name_plural = _("Связи характеристик с типами")

    def __str__(self):
        return f"{self.attribute} → {self.property_type}"


class AttributeChoice(BaseModel):
    attribute = models.ForeignKey(
        Attribute,
        related_name="choices",
        on_delete=models.CASCADE,
        verbose_name=_("Характеристика")
    )
    slug = models.SlugField(
        verbose_name=_("Slug")
    )
    sort_order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("Порядок")
    )

    class Meta:
        unique_together = ("attribute", "slug")
        verbose_name = _("Вариант выбора")
        verbose_name_plural = _("Варианты выбора")

    def __str__(self):
        translation = self.translations.filter(language=Language.RU).first()
        return translation.title if translation else self.slug


class AttributeChoiceTranslation(TranslationBase):
    choice = models.ForeignKey(
        AttributeChoice,
        related_name="translations",
        on_delete=models.CASCADE,
        verbose_name=_("Вариант")
    )
    title = models.CharField(
        max_length=150,
        verbose_name=_("Название")
    )

    class Meta:
        unique_together = ("choice", "language")
        verbose_name = _("Перевод варианта выбора")
        verbose_name_plural = _("Переводы вариантов выбора")

    def __str__(self):
        return self.title


class PropertyAttributeValue(BaseModel):
    property = models.ForeignKey(
        Property,
        related_name="attribute_values",
        on_delete=models.CASCADE,
        verbose_name=_("Объект")
    )
    attribute = models.ForeignKey(
        Attribute,
        related_name="values",
        on_delete=models.CASCADE,
        verbose_name=_("Характеристика")
    )
    value_integer = models.IntegerField(
        null=True, blank=True,
        verbose_name=_("Значение (целое число)")
    )
    value_decimal = models.DecimalField(
        max_digits=14, decimal_places=2,
        null=True, blank=True,
        verbose_name=_("Значение (дробное число)")
    )
    value_boolean = models.BooleanField(
        null=True, blank=True,
        verbose_name=_("Значение (да/нет)")
    )
    value_text = models.CharField(
        max_length=500, blank=True,
        verbose_name=_("Значение (текст)")
    )
    value_choice = models.ForeignKey(
        AttributeChoice,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Значение (вариант)")
    )

    class Meta:
        unique_together = ("property", "attribute")
        indexes = [
            models.Index(fields=["attribute", "value_integer"]),
            models.Index(fields=["attribute", "value_decimal"]),
            models.Index(fields=["attribute", "value_boolean"]),
            models.Index(fields=["attribute", "value_choice"]),
        ]
        verbose_name = _("Значение характеристики")
        verbose_name_plural = _("Значения характеристик")

    def __str__(self):
        return f"{self.property} — {self.attribute}"


# ==============================================================================
# Избранное
# ==============================================================================

class FavoriteProperty(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="favorites",
        on_delete=models.CASCADE,
        verbose_name=_("Пользователь")
    )
    property = models.ForeignKey(
        Property,
        related_name="favorited_by",
        on_delete=models.CASCADE,
        verbose_name=_("Объект")
    )

    class Meta:
        unique_together = ("user", "property")
        verbose_name = _("Избранное")
        verbose_name_plural = _("Избранное")

    def __str__(self):
        return f"{self.user} → {self.property}"


# ==============================================================================
# Настройки сайта (singleton)
# ==============================================================================

class SiteSettings(BaseModel):
    whatsapp_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Номер WhatsApp"),
        help_text=_("С кодом страны. Например: +995591234567")
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Номер телефона"),
        help_text=_("Отображается на сайте как контактный номер.")
    )
    email = models.EmailField(
        blank=True,
        verbose_name=_("Email")
    )

    class Meta:
        verbose_name = _("Настройки сайта")
        verbose_name_plural = _("Настройки сайта")

    def __str__(self):
        return "Настройки сайта"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)