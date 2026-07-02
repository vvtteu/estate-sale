from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from .widgets import LocationPickerWidget, LocationFormField
from django import forms

from .models import (
    DealType, DealTypeTranslation,
    PropertyType, PropertyTypeTranslation,
    PropertyStatus, PropertyStatusTranslation,
    ExchangeRate,
    Property, PropertyTranslation, PropertyImage,
    Attribute, AttributeTranslation,
    AttributePropertyType,
    AttributeChoice, AttributeChoiceTranslation,
    PropertyAttributeValue,
    FavoriteProperty,
    SiteSettings,
)


class PropertyAdminForm(forms.ModelForm):
    location = LocationFormField(
        required=False,
        label=_("Точка на карте"),
        widget=LocationPickerWidget(
            address_field="address",
            city_field="city",
            district_field="district",
            default_lat=41.7151,   # координаты твоего города по умолчанию
            default_lng=44.8271,
        ),
    )

    class Meta:
        model = Property
        fields = "__all__"


# ==============================================================================
# Тип сделки
# ==============================================================================

class DealTypeTranslationInline(TabularInline):
    model = DealTypeTranslation
    extra = 3
    max_num = 3
    verbose_name = _("Перевод")
    verbose_name_plural = _("Переводы (RU / EN / KA)")


@admin.register(DealType)
class DealTypeAdmin(ModelAdmin):
    list_display = ("__str__", "slug", "is_active", "sort_order")
    list_editable = ("is_active", "sort_order")
    inlines = [DealTypeTranslationInline]


# ==============================================================================
# Тип недвижимости (дерево)
# ==============================================================================

class PropertyTypeTranslationInline(TabularInline):
    model = PropertyTypeTranslation
    extra = 3
    max_num = 3
    verbose_name = _("Перевод")
    verbose_name_plural = _("Переводы (RU / EN / KA)")


@admin.register(PropertyType)
class PropertyTypeAdmin(ModelAdmin):
    list_display = ("__str__", "slug", "parent", "is_active", "sort_order")
    list_editable = ("is_active", "sort_order")
    list_filter = ("parent", "is_active")
    search_fields = ("slug", "translations__title")
    filter_horizontal = ("deal_types",)
    inlines = [PropertyTypeTranslationInline]


# ==============================================================================
# Статус объявления
# ==============================================================================

class PropertyStatusTranslationInline(TabularInline):
    model = PropertyStatusTranslation
    extra = 3
    max_num = 3
    verbose_name = _("Перевод")
    verbose_name_plural = _("Переводы (RU / EN / KA)")


@admin.register(PropertyStatus)
class PropertyStatusAdmin(ModelAdmin):
    list_display = ("__str__", "slug", "color", "sort_order")
    list_editable = ("sort_order",)
    inlines = [PropertyStatusTranslationInline]


# ==============================================================================
# Курс валют
# ==============================================================================

@admin.register(ExchangeRate)
class ExchangeRateAdmin(ModelAdmin):
    list_display = ("effective_date", "usd_to_gel")
    ordering = ("-effective_date",)


# ==============================================================================
# Характеристики
# ==============================================================================

class AttributeTranslationInline(TabularInline):
    model = AttributeTranslation
    extra = 3
    max_num = 3
    verbose_name = _("Перевод")
    verbose_name_plural = _("Переводы (RU / EN / KA)")


class AttributePropertyTypeInline(TabularInline):
    model = AttributePropertyType
    extra = 1
    verbose_name = _("Привязка к типу недвижимости")
    verbose_name_plural = _("Привязки к типам недвижимости")
    autocomplete_fields = ["property_type"]


@admin.register(Attribute)
class AttributeAdmin(ModelAdmin):
    list_display = ("__str__", "slug", "value_type", "unit", "is_filterable", "sort_order")
    list_editable = ("is_filterable", "sort_order")
    list_filter = ("value_type", "is_filterable")
    search_fields = ("slug", "translations__title")
    inlines = [AttributeTranslationInline, AttributePropertyTypeInline]


class AttributeChoiceTranslationInline(TabularInline):
    model = AttributeChoiceTranslation
    extra = 3
    max_num = 3
    verbose_name = _("Перевод")
    verbose_name_plural = _("Переводы (RU / EN / KA)")


@admin.register(AttributeChoice)
class AttributeChoiceAdmin(ModelAdmin):
    list_display = ("__str__", "attribute", "slug", "sort_order")
    list_filter = ("attribute",)
    search_fields = ("slug", "translations__title")
    inlines = [AttributeChoiceTranslationInline]


# ==============================================================================
# Объект недвижимости
# ==============================================================================

class PropertyTranslationInline(StackedInline):
    model = PropertyTranslation
    extra = 3
    max_num = 3
    verbose_name = _("Перевод")
    verbose_name_plural = _("Тексты объявления (RU / EN / KA)")


class PropertyImageInline(TabularInline):
    model = PropertyImage
    extra = 1
    fields = ("image", "is_main", "sort_order", "alt_text")
    verbose_name = _("Фотография")
    verbose_name_plural = _("Фотографии")


class PropertyAttributeValueInline(TabularInline):
    model = PropertyAttributeValue
    extra = 0
    autocomplete_fields = ["attribute", "value_choice"]
    fields = (
        "attribute",
        "value_integer",
        "value_decimal",
        "value_boolean",
        "value_text",
        "value_choice",
    )
    verbose_name = _("Характеристика")
    verbose_name_plural = _("Характеристики объекта")


@admin.register(Property)
class PropertyAdmin(ModelAdmin):   
    form = PropertyAdminForm
    list_display = (
        "__str__", "deal_type", "property_type", "city", "district",
        "price", "currency", "status", "is_published", "created_at",
    )
    list_filter = ("deal_type", "property_type", "status", "is_published", "currency")
    search_fields = ("slug", "translations__title", "address", "city", "district")
    list_editable = ("is_published",)
    readonly_fields = ("created_at", "updated_at", "created_by")
    fieldsets = (
        (_("Основное"), {"fields": ("deal_type", "property_type", "status", "slug")}),
        (_("Цена"), {"fields": ("price", "currency")}),
        (_("Местоположение"), {
            "description": _("Кликните на карте — адрес, город и район заполнятся автоматически. Поля можно поправить вручную."),
            "fields": ("location", "address", "city", "district"),
        }),
        (_("Параметры"), {"fields": ("area_total",)}),
        (_("Публикация"), {"fields": ("is_published", "published_at")}),
        (_("Служебное"), {"fields": ("created_by", "created_at", "updated_at"), "classes": ("collapse",)}),
    )
    inlines = [PropertyTranslationInline, PropertyImageInline, PropertyAttributeValueInline]

    def save_model(self, request, obj, form, change):
        if not obj.pk and not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

# ==============================================================================
# Избранное
# ==============================================================================

@admin.register(FavoriteProperty)
class FavoritePropertyAdmin(ModelAdmin):
    list_display = ("user", "property", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "property__slug")
    readonly_fields = ("user", "property", "created_at", "updated_at")

    def has_add_permission(self, request):
        return False


# ==============================================================================
# Настройки сайта
# ==============================================================================

@admin.register(SiteSettings)
class SiteSettingsAdmin(ModelAdmin):
    fieldsets = (
        (_("Контакты"), {
            "description": _("Эти данные отображаются на сайте во всех карточках объявлений."),
            "fields": ("whatsapp_number", "phone_number", "email")
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False