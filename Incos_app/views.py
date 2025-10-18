# app_name/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
import requests
import calendar
from datetime import date, timedelta
from django.db.models import Q
from .models import (
    Usuario,
    Prestatario,
    Articulo,
    Prestamo,
    Reserva,
)
from .forms import (
    CustomUserCreationForm,
    PrestatarioForm,
    ArticuloForm,
    PrestamoForm,
    ReservaForm,
)


# ============================================
# 1. DASHBOARD (Inicio)
# ============================================
@login_required
def inicio(request):
    """Vista principal (Dashboard) del sistema con datos dinámicos."""
    
    hoy = timezone.localdate()
    
    # 1. Estadísticas para las tarjetas
    total_prestamos_activos = Prestamo.objects.filter(estado='en_curso').count()
    devoluciones_este_mes = Prestamo.objects.filter(
        estado='devuelto',
        fecha_devolucion__month=hoy.month,
        fecha_devolucion__year=hoy.year
    ).count()
    reservas_pendientes = Reserva.objects.filter(estado='activo').count()
    prestamos_vencidos = Prestamo.objects.filter(
        estado='en_curso',
        fecha_prevista_devolucion__lt=hoy
    ).count()

    # 2. Lista de los últimos 5 préstamos activos para la tabla
    ultimos_prestamos_activos = Prestamo.objects.filter(estado='en_curso').order_by('-fecha_prestamo')[:5]

    context = {
        'titulo': 'Panel de Administración INCOS',
        'total_prestamos_activos': total_prestamos_activos,
        'devoluciones_este_mes': devoluciones_este_mes,
        'reservas_pendientes': reservas_pendientes,
        'prestamos_vencidos': prestamos_vencidos,
        'ultimos_prestamos_activos': ultimos_prestamos_activos,
    }
    return render(request, 'incos_app/home.html', context)


# ============================================
# 2. LOGIN PERSONALIZADO
# ============================================
class LoginView(DjangoLoginView):
    """Vista de login para los usuarios y administradores."""
    template_name = 'incos_app/Login/login_prestatario.html'

    def form_invalid(self, form):
        """Mostrar mensaje si el login falla."""
        messages.error(self.request, "Usuario o contraseña incorrectos.")
        return super().form_invalid(form)

# ============================================
# 3. GESTIÓN DE USUARIOS / ADMINISTRADORES
# ============================================
class AdminRegistrationView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Usuario
    form_class = CustomUserCreationForm
    template_name = 'incos_app/Usuario/admin_register.html'
    success_url = reverse_lazy('inicio')

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, "No tienes permiso para registrar nuevos administradores.")
        return redirect('inicio')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"✅ ¡La cuenta '{self.object.username}' fue creada correctamente!"
        )
        return response

    def form_invalid(self, form):
        messages.warning(self.request, "⚠️ Error al crear el usuario. Revisa los datos ingresados.")
        return super().form_invalid(form)


class UsuarioListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Usuario
    template_name = 'incos_app/Usuario/usuario_list.html'
    context_object_name = 'usuarios'

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, "Acceso denegado. Solo para Super Administradores.")
        return redirect('inicio')


class UsuarioUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Usuario
    form_class = CustomUserCreationForm
    template_name = 'incos_app/Usuario/usuario_form.html'
    success_url = reverse_lazy('usuario_list')

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, f"✅ ¡El usuario '{self.object.username}' fue actualizado correctamente!"
        )
        return response


class UsuarioDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Usuario
    template_name = 'incos_app/Usuario/usuario_confirm_delete.html'
    success_url = reverse_lazy('usuario_list')
    context_object_name = 'usuario'

    def test_func(self):
        return self.request.user.is_superuser and self.request.user != self.get_object()

    def form_valid(self, form):
        messages.error(
            self.request,
            f"🗑️ El usuario '{self.object.username}' ha sido eliminado del sistema."
        )
        return super().form_valid(form)

# ============================================
# 4. GESTIÓN DE PRESTATARIOS
# ============================================
class PrestatarioListView(LoginRequiredMixin, ListView):
    model = Prestatario
    template_name = 'incos_app/Prestatario/prestatario_list.html' # Ajusta la ruta si es necesario
    context_object_name = 'prestatarios'

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 1. Obtener parámetros de búsqueda y filtro
        search_query = self.request.GET.get('search', '')
        type_filter = self.request.GET.get('type', '')
        status_filter = self.request.GET.get('status', '')

        # 2. Filtrar por Búsqueda General (Nombre, C.I., Teléfono)
        if search_query:
            queryset = queryset.filter(
                Q(nombre__icontains=search_query) | 
                Q(apellidopaterno__icontains=search_query) |
                Q(apellidomaterno__icontains=search_query) |
                Q(ci__icontains=search_query) |
                Q(telefono__icontains=search_query)
            )

        # 3. Filtrar por Tipo de Prestatario
        if type_filter:
            # Asumiendo que el campo en el modelo se llama 'tipo'
            queryset = queryset.filter(tipo=type_filter) 

        # 4. Filtrar por Estado
        if status_filter:
            # Asumiendo que el campo en el modelo se llama 'estado'
            queryset = queryset.filter(estado=status_filter)
            
        # Opcional: ordenar por apellido para una mejor visualización
        return queryset.order_by('apellidopaterno', 'apellidomaterno')

class PrestatarioCreateView(LoginRequiredMixin, CreateView):
    model = Prestatario
    form_class = PrestatarioForm
    template_name = 'incos_app/Prestatario/prestatario_form.html'
    success_url = reverse_lazy('prestatario_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"✅ ¡El prestatario '{self.object.nombre} {self.object.apellidopaterno}' fue registrado!"
        )
        return response


class PrestatarioUpdateView(LoginRequiredMixin, UpdateView):
    model = Prestatario
    form_class = PrestatarioForm
    template_name = 'incos_app/Prestatario/prestatario_form.html'
    success_url = reverse_lazy('prestatario_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"✅ ¡Datos del prestatario '{self.object.nombre} {self.object.apellidopaterno}' actualizados!"
        )
        return response


class PrestatarioDeleteView(LoginRequiredMixin, DeleteView):
    model = Prestatario
    template_name = 'incos_app/Prestatario/prestatario_confirm_delete.html'
    success_url = reverse_lazy('prestatario_list')
    context_object_name = 'prestatario'

    def form_valid(self, form):
        prestatario_nombre = f"{self.get_object().nombre} {self.get_object().apellidopaterno}"
        messages.error(self.request, f"🗑️ El prestatario '{prestatario_nombre}' ha sido eliminado.")
        return super().form_valid(form)

# ============================================
# 5. GESTIÓN DE ARTÍCULOS
# ============================================
class ArticuloListView(LoginRequiredMixin, ListView):
    model = Articulo
    template_name = 'incos_app/Articulo/articulo_list.html'
    context_object_name = 'articulos' # Asegúrate de usar 'articulos' si no quieres cambiar el template

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 1. Obtener parámetros de búsqueda
        search_query = self.request.GET.get('search', '')
        status_filter = self.request.GET.get('status', '')

        # 2. Filtrar por Nombre
        if search_query:
            # Q busca en el nombre O en la descripción (o los campos que desees)
            queryset = queryset.filter(
                Q(nombre__icontains=search_query) | Q(descripcion__icontains=search_query)
            )

        # 3. Filtrar por Estado (Disponibilidad)
        if status_filter:
            if status_filter == 'available':
                # Disponibles: disponibilidad = True
                queryset = queryset.filter(disponibilidad=True)
            elif status_filter == 'on_loan':
                # En Préstamo: disponibilidad = False
                queryset = queryset.filter(disponibilidad=False)

        return queryset.order_by('nombre')


class ArticuloCreateView(LoginRequiredMixin, CreateView):
    model = Articulo
    form_class = ArticuloForm
    template_name = 'incos_app/Articulo/articulo_form.html'
    success_url = reverse_lazy('articulo_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"✅ ¡Artículo '{self.object.nombre}' registrado correctamente!")
        return response


class ArticuloUpdateView(LoginRequiredMixin, UpdateView):
    model = Articulo
    form_class = ArticuloForm
    template_name = 'incos_app/Articulo/articulo_form.html'
    success_url = reverse_lazy('articulo_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"✅ ¡Artículo '{self.object.nombre}' actualizado!")
        return response


class ArticuloDeleteView(LoginRequiredMixin, DeleteView):
    model = Articulo
    template_name = 'incos_app/Articulo/articulo_confirm_delete.html'
    success_url = reverse_lazy('articulo_list')
    context_object_name = 'articulo'

    def form_valid(self, form):
        messages.error(self.request, f"🗑️ Artículo '{self.get_object().nombre}' eliminado del inventario.")
        return super().form_valid(form)


# ============================================
# 7. GESTIÓN DE RESERVAS (CORREGIDA)
# ============================================

# 7.1 LISTAR RESERVAS (Read)
class ReservaListView(LoginRequiredMixin, ListView):
    model = Reserva
    template_name = 'incos_app/Reserva/reserva_list.html'
    context_object_name = 'reservas'

    def get_queryset(self):
        # Muestra activas y vencidas, ordenando por fecha_inicio
        queryset = Reserva.objects.exclude(estado='completado').order_by('fecha_inicio')
        
        # --- CORRECCIÓN CLAVE ---
        # Forzar la evaluación del QuerySet a una lista antes de devolverlo.
        # Esto puede obligar a la ORM a materializar los objetos como DateTimeField.
        return list(queryset)
        # ------------------------


# 7.2 CREAR RESERVA (Create)
class ReservaCreateView(LoginRequiredMixin, CreateView):
    model = Reserva
    form_class = ReservaForm
    template_name = 'incos_app/Reserva/reserva_form.html'
    success_url = reverse_lazy('reserva_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        
        # --- CAMBIO CLAVE: Usamos fecha_inicio en el mensaje ---
        messages.success(
            self.request,
            f"✅ Reserva de '{self.object.articulo.nombre}' del {self.object.fecha_inicio.strftime('%d/%m/%Y %H:%M')} registrada."
        )
        # ------------------------------------------------------
        
        return response
class ReservaUpdateView(LoginRequiredMixin, UpdateView):
    model = Reserva
    form_class = ReservaForm
    template_name = 'incos_app/Reserva/reserva_form.html' # O la plantilla de edición
    success_url = reverse_lazy('reserva_list')

# 7.3 CONVERTIR RESERVA A PRÉSTAMO (Action View)
class ReservaToPrestamoView(LoginRequiredMixin, View):

    def post(self, request, pk):
        reserva = get_object_or_404(Reserva, pk=pk)
        articulo = reserva.articulo
        prestatario = reserva.prestatario

        if reserva.estado != 'activo':
            messages.error(request, f"La Reserva #{reserva.id} no está activa.")
            return redirect('reserva_list')

        if not articulo.disponibilidad:
            messages.error(request, f"❌ El artículo {articulo.nombre} no está disponible.")
            return redirect('reserva_list')

        try:
            with transaction.atomic():
                # Crear el nuevo Préstamo
                Prestamo.objects.create(
                    articulo=articulo,
                    prestatario=prestatario,
                    usuario=request.user,
                    # --- CAMBIO CLAVE: Usamos fecha_fin para la devolución prevista ---
                    fecha_prevista_devolucion=reserva.fecha_fin,
                    # -----------------------------------------------------------------
                    observaciones=f"Generado a partir de la Reserva #{reserva.id}. {reserva.comentarios or ''}",
                    estado='en_curso'
                )

                # Marcar Artículo como NO DISPONIBLE
                articulo.disponibilidad = False
                articulo.save()

                # Marcar Reserva como COMPLETADA
                reserva.estado = 'completado'
                reserva.save()

                messages.success(
                    request,
                    f"✅ Reserva #{reserva.id} completada. Préstamo generado exitosamente."
                )
        except Exception as e:
            messages.error(request, f"Hubo un error al procesar la transacción: {e}")

        return redirect('prestamo_list')

# Las vistas PrestamoCreateView y PrestamoUpdateView no tienen referencias a 'fecha_reservada',
# por lo que no requieren correcciones en el código que me has proporcionado.

# ============================================
# 7.4. CALENDARIO DE RESERVAS (VISTA MEJORADA) - [Ya estaba corregida]
# ============================================
@login_required
def calendario_reservas(request, year=None, month=None):
    """Muestra un calendario con las reservas del mes actual."""

    hoy = timezone.localdate()
    if year is None or month is None:
        year = hoy.year
        month = hoy.month

    # 1. Obtener las reservas que INICIAN en este mes (para mostrarlas en el calendario)
    reservas_del_mes = Reserva.objects.filter(
        estado='activo',
        fecha_inicio__year=year,
        fecha_inicio__month=month
    ).order_by('fecha_inicio')

    # 2. Agrupar reservas por día de INICIO
    reservas_por_dia = {}
    for reserva in reservas_del_mes:
        dia = reserva.fecha_inicio.day
        if dia not in reservas_por_dia:
            reservas_por_dia[dia] = []
        reservas_por_dia[dia].append(reserva)

    # 3. Generar la matriz del calendario
    cal = calendar.Calendar(firstweekday=0) # 0 = Lunes
    month_calendar = cal.monthdayscalendar(year, month)
    
    # 4. Lógica de navegación (Mes anterior y siguiente)
    current_date = date(year, month, 1)
    
    # Usa timedelta directamente (ya importado arriba)
    prev_month_date = (current_date.replace(day=1) - timedelta(days=1)) 
    prev_month_nav = {
        'year': prev_month_date.year,
        'month': prev_month_date.month
    }

    if month == 12:
        next_month_date = date(year + 1, 1, 1)
    else:
        next_month_date = date(year, month + 1, 1)
    
    next_month_nav = {
        'year': next_month_date.year,
        'month': next_month_date.month
    }

    # 5. Preparar el contexto
    context = {
        'hoy': hoy,
        'mes_nombre': current_date.strftime("%B").capitalize(),
        'año': year,
        'mes': month,
        'reservas_por_dia': reservas_por_dia,
        'month_calendar': month_calendar,
        'form': ReservaForm(),
        'prev_month_nav': prev_month_nav,
        'next_month_nav': next_month_nav,
    }

    return render(request, 'incos_app/Reserva/reserva_calendario.html', context)
# ============================================
# 6. GESTIÓN DE PRÉSTAMOS
# ============================================
class PrestamoListView(LoginRequiredMixin, ListView):
    model = Prestamo
    template_name = 'incos_app/Prestamo/prestamo_list.html'
    context_object_name = 'prestamos'

    def get_queryset(self):
        return Prestamo.objects.exclude(estado='devuelto')


class PrestamoCreateView(LoginRequiredMixin, CreateView):
    model = Prestamo
    form_class = PrestamoForm
    template_name = 'incos_app/Prestamo/prestamo_form.html'
    success_url = reverse_lazy('prestamo_list')

    def form_valid(self, form):
        with transaction.atomic():
            form.instance.usuario = self.request.user
            response = super().form_valid(form)
            articulo = form.instance.articulo
            articulo.disponibilidad = False
            articulo.save()
            messages.success(
                self.request,
                f"✅ Préstamo de '{articulo.nombre}' registrado. Artículo marcado como NO disponible."
            )
            # Aquí iría la lógica de notificación de Telegram si la estás usando
            # ...
            return response


# --- CLASE FALTANTE QUE CAUSA EL ERROR (AttributeError) ---
class PrestamoUpdateView(LoginRequiredMixin, UpdateView):
    model = Prestamo 
    form_class = PrestamoForm 
    template_name = 'incos_app/Prestamo/prestamo_form.html' 
    success_url = reverse_lazy('prestamo_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"🔄 ¡El préstamo #{self.object.id} fue modificado y la fecha de devolución fue actualizada!"
        )
        return response
# ----------------------------------------------------------


class PrestamoDevolucionView(LoginRequiredMixin, View):
    def post(self, request, pk):
        prestamo = get_object_or_404(Prestamo, pk=pk)
        articulo = prestamo.articulo

        with transaction.atomic():
            prestamo.estado = 'devuelto'
            # Es mejor usar timezone.now() para datetimefield, o timezone.localdate() para datefield
            # Asumo que fecha_devolucion es un DateTimeField, por lo que uso timezone.now()
            prestamo.fecha_devolucion = timezone.now() 
            prestamo.save()

            articulo.disponibilidad = True
            articulo.save()

            messages.success(
                request,
                f"✅ Devolución de '{articulo.nombre}' registrada. Artículo disponible nuevamente."
            )

        return redirect('prestamo_list')

# ... (Aquí continuaría la gestión de Reservas, etc.)