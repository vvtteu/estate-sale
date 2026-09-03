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