from django import template
from django.utils.translation import get_language

register = template.Library()

@register.simple_tag(takes_context=True)
def change_lang_url(context, lang):
    """Возвращает текущий URL с заменённым языковым префиксом."""
    request = context.get("request")
    if not request:
        return "/"
    
    path = request.get_full_path()
    current_lang = get_language()
    
    # Убираем текущий языковой префикс если есть
    if current_lang and current_lang != "ru":
        if path.startswith(f"/{current_lang}/"):
            path = path[len(f"/{current_lang}"):]
    
    # Добавляем новый префикс если не русский
    if lang == "ru":
        return path or "/"
    else:
        return f"/{lang}{path}"