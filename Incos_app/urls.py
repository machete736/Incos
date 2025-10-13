# app_name/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # ============================================
    # AUTENTICACIÓN
    # ============================================
    path('', views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    # Recuperación de contraseña
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # ============================================
    # DASHBOARD
    # ============================================
    path('dashboard/', views.inicio, name='inicio'),

    # ============================================
    # GESTIÓN DE USUARIOS / ADMINISTRADORES
    # ============================================
    path('usuarios/', views.UsuarioListView.as_view(), name='usuario_list'),
    path('usuarios/crear/', views.AdminRegistrationView.as_view(), name='usuario_create'),
    path('usuarios/editar/<int:pk>/', views.UsuarioUpdateView.as_view(), name='usuario_update'),
    path('usuarios/eliminar/<int:pk>/', views.UsuarioDeleteView.as_view(), name='usuario_delete'),

    # ============================================
    # GESTIÓN DE PRESTATARIOS (Estudiantes/Profesores)
    # ============================================
    path('prestatarios/', views.PrestatarioListView.as_view(), name='prestatario_list'),
    path('prestatarios/crear/', views.PrestatarioCreateView.as_view(), name='prestatario_create'),
    path('prestatarios/editar/<int:pk>/', views.PrestatarioUpdateView.as_view(), name='prestatario_update'),
    path('prestatarios/eliminar/<int:pk>/', views.PrestatarioDeleteView.as_view(), name='prestatario_delete'),
path('prestatarios/registro/', views.PrestatarioCreateView.as_view(), name='registro_prestatario'),

    # ============================================
    # GESTIÓN DE RECURSOS / ARTÍCULOS
    # ============================================
    path('recursos/', views.ArticuloListView.as_view(), name='articulo_list'),
    path('recursos/crear/', views.ArticuloCreateView.as_view(), name='articulo_create'),
    path('recursos/editar/<int:pk>/', views.ArticuloUpdateView.as_view(), name='articulo_update'),
    path('recursos/eliminar/<int:pk>/', views.ArticuloDeleteView.as_view(), name='articulo_delete'),

    # ============================================
    # GESTIÓN DE PRÉSTAMOS
    # ============================================
    path('prestamos/', views.PrestamoListView.as_view(), name='prestamo_list'),
    path('prestamos/crear/', views.PrestamoCreateView.as_view(), name='prestamo_create'),
    path('prestamos/devolver/<int:pk>/', views.PrestamoDevolucionView.as_view(), name='prestamo_devolver'),

    # ============================================
    # GESTIÓN DE RESERVAS
    # ============================================
    path('reservas/', views.ReservaListView.as_view(), name='reserva_list'),
    path('reservas/crear/', views.ReservaCreateView.as_view(), name='reserva_create'),
    path('reservas/calendario/', views.calendario_reservas, name='reserva_calendario'),
    path('reservas/convertir/<int:pk>/', views.ReservaToPrestamoView.as_view(), name='reserva_to_prestamo'),
]
