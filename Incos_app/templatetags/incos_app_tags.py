from django import template
from django.urls import reverse

register = template.Library()

@register.simple_tag
def active_link(request, view_name):
    """
    Devuelve 'active' si la URL actual coincide con el nombre de la vista, 
    o si el path contiene una palabra clave asociada.
    """
    if request.path == reverse(view_name):
        return 'active'
    
    # Lógica especial para rutas que contienen una palabra
    keyword_map = {
        'prestatario_list': 'prestatarios',
        'reserva_calendario': 'reservas',
        'articulo_list': 'recursos',
        'prestamo_list': 'prestamos',
        'usuario_list': 'usuarios',
    }
    
    if view_name in keyword_map and keyword_map[view_name] in request.path:
        return 'active'
        
    return ''