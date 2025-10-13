# app_name/views.py

from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db import transaction
from django.utils import timezone

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
    """Vista principal (Dashboard) del sistema."""
    context = {'titulo': 'Panel de Administración INCOS'}
    return render(request, 'Incos_app/home.html', context)

# ============================================
# 2. LOGIN PERSONALIZADO
# ============================================
class LoginView(DjangoLoginView):
    """Vista de login para los usuarios y administradores."""
    template_name = 'Incos_app/Login/login_prestatario.html'

# ============================================
# 3. GESTIÓN DE USUARIOS / ADMINISTRADORES
# ============================================
class AdminRegistrationView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Usuario
    form_class = CustomUserCreationForm
    template_name = 'Incos_app/Usuario/admin_register.html'
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
    template_name = 'Incos_app/Usuario/usuario_list.html'
    context_object_name = 'usuarios'

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, "Acceso denegado. Solo para Super Administradores.")
        return redirect('inicio')


class UsuarioUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Usuario
    form_class = CustomUserCreationForm
    template_name = 'Incos_app/Usuario/usuario_form.html'
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
    template_name = 'Incos_app/Usuario/usuario_confirm_delete.html'
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
    template_name = 'Incos_app/Prestatario/prestatario_list.html'
    context_object_name = 'prestatarios'


class PrestatarioCreateView(LoginRequiredMixin, CreateView):
    model = Prestatario
    form_class = PrestatarioForm
    template_name = 'Incos_app/Prestatario/prestatario_form.html'
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
    template_name = 'Incos_app/Prestatario/prestatario_form.html'
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
    template_name = 'Incos_app/Prestatario/prestatario_confirm_delete.html'
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
    template_name = 'Incos_app/Articulo/articulo_list.html'
    context_object_name = 'articulos'


class ArticuloCreateView(LoginRequiredMixin, CreateView):
    model = Articulo
    form_class = ArticuloForm
    template_name = 'Incos_app/Articulo/articulo_form.html'
    success_url = reverse_lazy('articulo_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"✅ ¡Artículo '{self.object.nombre}' registrado correctamente!")
        return response


class ArticuloUpdateView(LoginRequiredMixin, UpdateView):
    model = Articulo
    form_class = ArticuloForm
    template_name = 'Incos_app/Articulo/articulo_form.html'
    success_url = reverse_lazy('articulo_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"✅ ¡Artículo '{self.object.nombre}' actualizado!")
        return response


class ArticuloDeleteView(LoginRequiredMixin, DeleteView):
    model = Articulo
    template_name = 'Incos_app/Articulo/articulo_confirm_delete.html'
    success_url = reverse_lazy('articulo_list')
    context_object_name = 'articulo'

    def form_valid(self, form):
        messages.error(self.request, f"🗑️ Artículo '{self.get_object().nombre}' eliminado del inventario.")
        return super().form_valid(form)

# ============================================
# 6. GESTIÓN DE PRÉSTAMOS
# ============================================
class PrestamoListView(LoginRequiredMixin, ListView):
    model = Prestamo
    template_name = 'Incos_app/Prestamo/prestamo_list.html'
    context_object_name = 'prestamos'

    def get_queryset(self):
        return Prestamo.objects.exclude(estado='devuelto')


class PrestamoCreateView(LoginRequiredMixin, CreateView):
    model = Prestamo
    form_class = PrestamoForm
    template_name = 'Incos_app/Prestamo/prestamo_form.html'
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
            return response


class PrestamoDevolucionView(LoginRequiredMixin, View):
    def post(self, request, pk):
        prestamo = get_object_or_404(Prestamo, pk=pk)
        articulo = prestamo.articulo

        with transaction.atomic():
            prestamo.estado = 'devuelto'
            prestamo.fecha_devolucion = timezone.now().date()
            prestamo.save()

            articulo.disponibilidad = True
            articulo.save()

            messages.success(
                request,
                f"✅ Devolución de '{articulo.nombre}' registrada. Artículo disponible nuevamente."
            )

        return redirect('prestamo_list')


# ============================================
# 7. GESTIÓN DE RESERVAS
# ============================================

# 7.1 LISTAR RESERVAS (Read)
class ReservaListView(LoginRequiredMixin, ListView):
    model = Reserva
    template_name = 'Incos_app/Reserva/reserva_list.html'
    context_object_name = 'reservas'

    def get_queryset(self):
        # Muestra activas y vencidas
        return Reserva.objects.exclude(estado='completado').order_by('fecha_reservada')


# 7.2 CREAR RESERVA (Create)
class ReservaCreateView(LoginRequiredMixin, CreateView):  # <--- CLASE FALTANTE/ERROR DE CARGA
    model = Reserva
    form_class = ReservaForm
    template_name = 'Incos_app/Reserva/reserva_form.html'  # Usaremos este en caso de error en el modal
    success_url = reverse_lazy('reserva_list')

    def form_valid(self, form):
        # El estado por defecto es 'activo', no necesita ser asignado
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"✅ Reserva de '{self.object.articulo.nombre}' para {self.object.fecha_reservada} registrada."
        )
        return response


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
                    fecha_prevista_devolucion=reserva.fecha_reservada,
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

# ============================================
# 7.4. CALENDARIO DE RESERVAS (Vista de visualización)
# ============================================
@login_required
def calendario_reservas(request):
    """Muestra un calendario con las reservas del mes actual."""

    hoy = timezone.localdate()
    mes = hoy.month
    año = hoy.year

    reservas_del_mes = Reserva.objects.filter(
        estado='activo',
        fecha_reservada__year=año,
        fecha_reservada__month=mes
    ).order_by('fecha_reservada')

    reservas_por_dia = {}
    for reserva in reservas_del_mes:
        dia = reserva.fecha_reservada.day
        if dia not in reservas_por_dia:
            reservas_por_dia[dia] = []
        reservas_por_dia[dia].append(reserva)

    context = {
        'hoy': hoy,
        'mes_nombre': hoy.strftime("%B").capitalize(),
        'año': año,
        'mes': mes,
        'reservas_por_dia': reservas_por_dia,
        'calendar': date(año, mes, 1).weekday(), # 0=Lun, 6=Dom
        'dias_mes': (date(año, mes + 1, 1) - date(año, mes, 1)).days if mes < 12 else (
                    date(año + 1, 1, 1) - date(año, 12, 1)).days,
        'form': ReservaForm(),  # Formulario necesario para el modal
    }

    return render(request, 'Incos_app/Reserva/reserva_calendario.html', context)