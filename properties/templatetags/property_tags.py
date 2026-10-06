from django import template
from django.utils.translation import get_language

register = template.Library()


@register.filter
def trans_title(property_obj):
    """Возвращает заголовок объекта на текущем языке."""
    lang = get_language()[:2]  # 'ru', 'en', 'ka'
    translation = property_obj.translations.filter(language=lang).first()
    if not translation:
        # fallback на русский если перевода нет
        translation = property_obj.translations.filter(language="ru").first()
    return translation.title if translation else property_obj.slug


@register.filter
def trans_description(property_obj):
    """Возвращает описание объекта на текущем языке."""
    lang = get_language()[:2]
    translation = property_obj.translations.filter(language=lang).first()
    if not translation:
        translation = property_obj.translations.filter(language="ru").first()
    return translation.description if translation else ""


@register.filter
def trans_address(property_obj):
    """Возвращает адрес объекта на текущем языке."""
    lang = get_language()[:2]
    translation = property_obj.translations.filter(language=lang).first()
    if not translation:
        translation = property_obj.translations.filter(language="ru").first()
    return translation.address_text if translation else property_obj.address

@register.filter
def trans_status(property_obj):
    """Возвращает статус на текущем языке."""
    lang = get_language()[:2]
    translation = property_obj.status.translations.filter(language=lang).first()
    if not translation:
        translation = property_obj.status.translations.filter(language="ru").first()
    return translation.title if translation else property_obj.status.slug

@register.filter
def trans_deal_type(property_obj):
    """Возвращает тип сделки на текущем языке."""
    lang = get_language()[:2]
    translation = property_obj.deal_type.translations.filter(language=lang).first()
    if not translation:
        translation = property_obj.deal_type.translations.filter(language="ru").first()
    return translation.title if translation else property_obj.deal_type.slug

@register.filter
def trans_type_name(property_type_obj):
    """Возвращает название типа недвижимости на текущем языке."""
    lang = get_language()[:2]
    translation = property_type_obj.translations.filter(language=lang).first()
    if not translation:
        translation = property_type_obj.translations.filter(language="ru").first()
    return translation.title if translation else property_type_obj.slug

@register.filter
def trans_attr_name(attr_val):
    """Возвращает название характеристики на текущем языке."""
    lang = get_language()[:2]
    translation = attr_val.attribute.translations.filter(language=lang).first()
    if not translation:
        translation = attr_val.attribute.translations.filter(language="ru").first()
    return translation.title if translation else attr_val.attribute.slug


@register.filter
def trans_attr_value(attr_val):
    """Возвращает значение характеристики на текущем языке."""
    # Для вариантов выбора — берём перевод
    if attr_val.value_choice:
        lang = get_language()[:2]
        translation = attr_val.value_choice.translations.filter(language=lang).first()
        if not translation:
            translation = attr_val.value_choice.translations.filter(language="ru").first()
        return translation.title if translation else attr_val.value_choice.slug
    
    # Для boolean — переводим да/нет
    if attr_val.value_boolean is not None:
        if get_language()[:2] == "en":
            return "Yes" if attr_val.value_boolean else "No"
        elif get_language()[:2] == "ka":
            return "დიახ" if attr_val.value_boolean else "არა"
        return "Да" if attr_val.value_boolean else "Нет"
    
    # Для остальных типов — просто значение
    if attr_val.value_integer is not None:
        return attr_val.value_integer
    if attr_val.value_decimal is not None:
        return attr_val.value_decimal
    return attr_val.value_text

@register.filter
def trans_property_type(property_obj):
    """Возвращает тип недвижимости на текущем языке."""
    lang = get_language()[:2]
    pt = property_obj.property_type
    translation = pt.translations.filter(language=lang).first()
    if not translation:
        translation = pt.translations.filter(language="ru").first()
    title = translation.title if translation else pt.slug

    if pt.parent:
        parent_trans = pt.parent.translations.filter(language=lang).first()
        if not parent_trans:
            parent_trans = pt.parent.translations.filter(language="ru").first()
        parent_title = parent_trans.title if parent_trans else pt.parent.slug
        return f"{parent_title} — {title}"

    return title