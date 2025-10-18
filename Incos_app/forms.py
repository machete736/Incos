# app_name/forms.py

from django import forms
from .models import Usuario, Prestatario, Reserva, Prestamo, Articulo
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm

# --------------------------------------------
# Formularios para la gestión de Administradores
# --------------------------------------------

class CustomUserCreationForm(UserCreationForm):
    """
    Formulario para la creación de nuevos usuarios/administradores (basado en AbstractUser).
    """
    # Los labels están correctos para que coincidan con el modelo Usuario
    nombre = forms.CharField(max_length=100, label="Nombre(s)")
    apellido_paterno = forms.CharField(max_length=50, label="Apellido Paterno")
    apellido_materno = forms.CharField(max_length=50, required=False, label="Apellido Materno")
    email = forms.EmailField(label="Correo institucional")
    role = forms.ChoiceField(choices=Usuario.ROLES, label="Rol")

    class Meta:
        model = Usuario
        # Incluye el campo 'username' que hereda de AbstractUser
        fields = ('username', 'nombre', 'apellido_paterno', 'apellido_materno', 'email', 'role',)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.nombre = self.cleaned_data["nombre"]
        user.apellido_paterno = self.cleaned_data["apellido_paterno"]
        user.apellido_materno = self.cleaned_data["apellido_materno"]
        user.email = self.cleaned_data["email"]
        user.role = self.cleaned_data["role"]

        # Configura las propiedades de administración por defecto
        user.is_active = True
        user.is_staff = True

        if commit:
            user.save()
        return user
# --------------------------------------------
# Formularios para la gestión de Prestatarios
# --------------------------------------------

class PrestatarioForm(forms.ModelForm):
    """
    Formulario para crear y actualizar prestatarios (alumnos/profesores).
    """

    class Meta:
        model = Prestatario
        fields = ['nombre', 'apellidopaterno', 'apellidomaterno', 'ci', 'telefono', 'email', 'telegram_chat_id','tipo', 'carrera_o_area',
                  'estado']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            # Puedes añadir más widgets aquí para estilos o tipos de input específicos
        }

# --------------------------------------------
# Formularios para la gestión de Artículos
# --------------------------------------------

class ArticuloForm(forms.ModelForm):
    class Meta:
        model = Articulo
        fields = ['nombre', 'categoria', 'descripcion', 'disponibilidad', 'ubicacion']
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }


class PrestamoForm(forms.ModelForm):
    # ... (Definición de fecha_prevista_devolucion) ...
    fecha_prevista_devolucion = forms.DateTimeField(
        label="Fecha y hora prevista de devolución",
        input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={'type': 'datetime-local'}
        )
    )

    class Meta:
        model = Prestamo
        fields = ['articulo', 'prestatario', 'fecha_prevista_devolucion', 'observaciones']
        widgets = {
            'observaciones': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 🟢 FILTRO PARA PRÉSTAMO: Solo artículos disponibles
        self.fields['articulo'].queryset = Articulo.objects.filter(disponibilidad=True)
        self.fields['articulo'].widget.attrs['class'] = 'form-control'
        self.fields['prestatario'].widget.attrs['class'] = 'form-control'


    def clean_fecha_prevista_devolucion(self):
        fecha_prevista = self.cleaned_data.get('fecha_prevista_devolucion')
        if fecha_prevista and fecha_prevista < timezone.now():
            raise forms.ValidationError("La fecha y hora de devolución no puede ser en el pasado.")
        return fecha_prevista


class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['articulo', 'prestatario', 'fecha_inicio', 'fecha_fin', 'comentarios']
        widgets = {
            'fecha_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'fecha_fin': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'comentarios': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'articulo': forms.Select(attrs={'class': 'form-control'}),
            'prestatario': forms.Select(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 🟢 FILTRO PARA RESERVA: Solo artículos disponibles (¡ESTA ES LA CORRECCIÓN CLAVE!)
        self.fields['articulo'].queryset = Articulo.objects.filter(disponibilidad=True)