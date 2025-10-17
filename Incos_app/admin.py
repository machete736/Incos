# Incos_app/admin.py

from django.contrib import admin
from .models import Usuario, Prestatario, Articulo, Prestamo, Reserva

# Registramos cada modelo para que aparezca en el panel de administración.
# Usar @admin.register es una forma moderna y limpia de hacerlo.

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'nombre_completo', 'email', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser')
    search_fields = ('username', 'nombre', 'apellido_paterno', 'email')

@admin.register(Prestatario)
class PrestatarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellidopaterno', 'ci', 'tipo', 'estado')
    list_filter = ('tipo', 'estado')
    search_fields = ('nombre', 'apellidopaterno', 'ci')

@admin.register(Articulo)
class ArticuloAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'disponibilidad')
    list_filter = ('categoria', 'disponibilidad')
    search_fields = ('nombre',)

@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'prestatario', 'articulo', 'fecha_prestamo', 'fecha_prevista_devolucion', 'estado')
    list_filter = ('estado',)
    search_fields = ('prestatario__nombre', 'articulo__nombre')

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'prestatario', 'articulo', 'fecha_reservada', 'estado')
    list_filter = ('estado',)
    search_fields = ('prestatario__nombre', 'articulo__nombre')