# app_name/forms.py

from django import forms
from .models import Usuario, Prestatario, Reserva, Prestamo, Articulo

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
        fields = ['nombre', 'apellidopaterno', 'apellidomaterno', 'ci', 'telefono', 'email', 'tipo', 'carrera_o_area',
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
    """
    Formulario para crear y actualizar artículos.
    """

    class Meta:
        model = Articulo
        fields = ['nombre', 'categoria', 'descripcion', 'disponibilidad', 'ubicacion']
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }


class PrestamoForm(forms.ModelForm):
    class Meta:
        model = Prestamo
        # El campo 'usuario' (admin) se asigna en la vista, no en el formulario.
        # El campo 'estado' y 'fecha_devolucion' no se usan al crear.
        fields = ['articulo', 'prestatario', 'fecha_prevista_devolucion', 'observaciones']
        widgets = {
            'fecha_prevista_devolucion': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra el queryset de Artículos para que solo muestre los que tienen disponibilidad=True
        self.fields['articulo'].queryset = Articulo.objects.filter(disponibilidad=True)

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        # Excluye 'fecha_reserva' (auto_now_add) y 'estado' (default='activo')
        fields = ['articulo', 'prestatario', 'fecha_reservada', 'comentarios']
        widgets = {
            'fecha_reservada': forms.DateInput(attrs={'type': 'date'}),
        }