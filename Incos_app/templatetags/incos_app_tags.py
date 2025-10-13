# C:\Incos\Incos_app\templatetags\incos_app_tags.py

from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Permite buscar un elemento en un diccionario por clave."""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None


@register.filter
def make_list(value):
    """Convierte una cadena de texto en una lista (útil para el ciclo for)."""
    return list(value)


@register.filter
def times(value, arg):
    """Multiplica el valor por el argumento (para ciclos de calendario)."""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0  # Devuelve 0 en caso de error para evitar fallos


@register.filter
def add(value, arg):
    """Suma el valor por el argumento, manejando el caso de resta (usando '-' como separador)."""
    try:
        if isinstance(arg, str) and arg.startswith('-'):
            return int(value) - int(arg[1:])
        return int(value) + int(arg)
    except (ValueError, TypeError):
        return value  # Devuelve el valor original en caso de error