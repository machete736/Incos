
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone
class Usuario(AbstractUser):
    """
    Representa a los administradores del sistema INCOS.
    Hereda de AbstractUser.
    """

    ROLES = [
        ('admin', 'Administrador'),
        ('superadmin', 'Super Administrador'),
    ]

    # Campos personalizados
    nombre = models.CharField("Nombre(s)", max_length=100)
    apellido_paterno = models.CharField("Apellido paterno", max_length=50)
    apellido_materno = models.CharField("Apellido materno", max_length=50, blank=True, null=True)
    email = models.EmailField("Correo institucional", unique=True)
    role = models.CharField("Rol", max_length=20, choices=ROLES, default='admin')
    created_at = models.DateTimeField("Fecha de creación", auto_now_add=True)

    # Campos de AbstractUser que no usaremos:
    first_name = None
    last_name = None

    # ========================================================
    # CORRECCIÓN DE CONFLICTOS: related_name (FIELDS.E304)
    # ========================================================
    # Necesario para evitar conflictos con el modelo User predeterminado
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="incos_admin_groups",  # <-- Nombre único para evitar choque
        related_query_name="incos_admin",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="incos_admin_permissions",  # <-- Nombre único para evitar choque
        related_query_name="incos_admin",
    )
    # ========================================================


    def nombre_completo(self):
        """Devuelve el nombre completo en formato estándar institucional."""
        ap_materno = f" {self.apellido_materno}" if self.apellido_materno else ""
        return f"{self.apellido_paterno}{ap_materno}, {self.nombre}"

    def __str__(self):
        return f"{self.nombre_completo()} ({self.get_role_display()})"

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['apellido_paterno', 'apellido_materno', 'nombre']


# ============================================
# MODELO DE PRESTATARIOS (ALUMNOS/PROFESORES)
# ============================================
class Prestatario(models.Model):
    """
    Representa a las personas que solicitan préstamos o reservas.
    """
    TIPOS = [
        ('estudiante', 'Estudiante'),
        ('profesor', 'Profesor'),
        ('otro', 'Otro'),
    ]

    ESTADOS = [
        ('activo', 'Activo'),
        ('suspendido', 'Suspendido'),
    ]

    nombre = models.CharField("Nombre completo", max_length=100)
    apellidopaterno = models.CharField("Apellido Paterno", max_length=100)
    apellidomaterno = models.CharField("Apellido Materno", max_length=100)
    ci = models.CharField("Cédula de identidad", max_length=20, unique=True)
    telefono = models.CharField("Teléfono", max_length=20, blank=True, null=True)
    telegram_chat_id = models.CharField(
        "Telegram Chat ID", 
        max_length=50, 
        blank=True, 
        null=True, 
        help_text="El ID único del chat de Telegram del usuario para notificaciones."
    )
    email = models.EmailField("Correo electrónico", blank=True, null=True)
    tipo = models.CharField("Tipo de prestatario", max_length=30, choices=TIPOS)
    carrera_o_area = models.CharField("Carrera o área", max_length=100, blank=True, null=True)
    estado = models.CharField("Estado", max_length=20, choices=ESTADOS, default='activo')
    fecha_registro = models.DateTimeField("Fecha de registro", auto_now_add=True)

    
    def __str__(self):
        return f"{self.nombre} ({self.tipo})"

    class Meta:
        verbose_name = "Prestatario"
        verbose_name_plural = "Prestatarios"
        ordering = ['nombre']


# ============================================
# MODELO DE ARTÍCULOS (LLAVES, AULAS, DOCUMENTOS, ETC.)
# ============================================
class Articulo(models.Model):
    """
    Representa los artículos disponibles para préstamo o reserva.
    """
    CATEGORIAS = [
        ('llave', 'Llave'),
        ('aula', 'Aula'),
        ('documento', 'Documento'),
        ('equipo', 'Equipo'),
        ('proyecto', 'Proyecto'),
        ('otro', 'Otro'),
    ]

    nombre = models.CharField("Nombre del artículo", max_length=100)
    categoria = models.CharField("Categoría", max_length=50, choices=CATEGORIAS)
    descripcion = models.TextField("Descripción", blank=True, null=True)
    disponibilidad = models.BooleanField("Disponible", default=True)
    ubicacion = models.CharField("Ubicación física", max_length=100, blank=True, null=True)
    fecha_registro = models.DateTimeField("Fecha de registro", auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.categoria})"

    class Meta:
        verbose_name = "Artículo"
        verbose_name_plural = "Artículos"
        ordering = ['nombre']


# ============================================
# MODELO DE PRÉSTAMOS
# ============================================
class Prestamo(models.Model):
    """
    Registra los préstamos realizados por los administradores a los prestatarios.
    """
    ESTADOS = [  # <--- ¡ESTO ESTABA FALTANDO O INCOMPLETO!
        ('en_curso', 'En curso'),
        ('devuelto', 'Devuelto'),
        ('retrasado', 'Retrasado'),
        ('perdido', 'Perdido'),
    ]

    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE, verbose_name="Artículo")
    prestatario = models.ForeignKey(Prestatario, on_delete=models.CASCADE, verbose_name="Prestatario")

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Administrador responsable"
    )

    fecha_prestamo = models.DateTimeField("Fecha de préstamo", auto_now_add=True)

    # <--- ¡ASEGÚRATE DE QUE ESTOS CUATRO CAMPOS EXISTAN!
    fecha_prevista_devolucion = models.DateTimeField("Fecha y hora prevista de devolución")
    fecha_devolucion = models.DateTimeField("Fecha y hora real de devolución", blank=True, null=True)
    estado = models.CharField("Estado del préstamo", max_length=20, choices=ESTADOS, default='en_curso')
    observaciones = models.TextField("Observaciones", blank=True, null=True)

    # ------------------------------------------------------------------

    def __str__(self):
        return f"Préstamo #{self.id} - {self.articulo.nombre} a {self.prestatario.nombre}"

    class Meta:
        verbose_name = "Préstamo"
        verbose_name_plural = "Préstamos"
        ordering = ['-fecha_prestamo']
class Reserva(models.Model):
    """
    Registra las reservas de artículos con rango de fecha y hora.
    """
    ESTADOS = [
        ('activo', 'Activo'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
        ('vencido', 'Vencido'),
    ]

    articulo = models.ForeignKey('Articulo', on_delete=models.CASCADE, verbose_name="Artículo reservado")
    prestatario = models.ForeignKey('Prestatario', on_delete=models.CASCADE, verbose_name="Prestatario")
    fecha_reserva = models.DateTimeField("Fecha de solicitud", auto_now_add=True)

    # --- CAMBIOS CLAVE: Usamos DateTimeField para incluir la hora ---
    fecha_inicio = models.DateTimeField("Fecha y hora de inicio de la reserva")
    fecha_fin = models.DateTimeField("Fecha y hora de fin de la reserva")
    # -------------------------------------------------------------

    estado = models.CharField("Estado de la reserva", max_length=20, choices=ESTADOS, default='activo')
    comentarios = models.TextField("Comentarios", blank=True, null=True)

    def clean(self):
        # Validación 1: Fecha de fin no puede ser anterior a la de inicio
        if self.fecha_fin and self.fecha_inicio and self.fecha_fin < self.fecha_inicio:
            raise ValidationError("La fecha y hora de fin no puede ser anterior a la de inicio.")

        # Validación 2: NO permitir crear reservas para fechas u horas pasadas
        # Usamos self.pk is None para que solo se aplique al CREAR (no al editar)
        if self.pk is None and self.fecha_inicio and self.fecha_inicio < timezone.now():
            raise ValidationError("No se pueden crear reservas para fechas u horas pasadas. La reserva debe iniciar en el futuro.")

    def __str__(self):
        return f"Reserva #{self.id} - {self.articulo.nombre} ({self.estado})"

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ['fecha_inicio']
# ============================================
# (OPCIONAL) INTERACCIONES DEL CHATBOT
# ============================================
class InteraccionChatbot(models.Model):
    """
    Guarda el historial de mensajes del chatbot con los prestatarios.
    (Útil para una futura integración con IA o WhatsApp)
    """
    prestatario = models.ForeignKey(Prestatario, on_delete=models.CASCADE, verbose_name="Prestatario")
    mensaje_usuario = models.TextField("Mensaje del usuario")
    respuesta_bot = models.TextField("Respuesta del chatbot", blank=True, null=True)
    fecha = models.DateTimeField("Fecha de interacción", auto_now_add=True)

    def __str__(self):
        return f"Chat con {self.prestatario.nombre} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        verbose_name = "Interacción del chatbot"
        verbose_name_plural = "Interacciones del chatbot"
        ordering = ['-fecha']
