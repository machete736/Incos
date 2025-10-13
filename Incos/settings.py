"""
Django settings for Incos project.

Configuración adaptada para usar Neon PostgreSQL
y variables de entorno (.env) en Codespaces o entornos locales.
"""

from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url

# ============================================================
# RUTAS BASE
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar variables de entorno (.env)
load_dotenv(BASE_DIR / ".env")


# ============================================================
# CONFIGURACIÓN BÁSICA
# ============================================================
SECRET_KEY = os.getenv('SECRET_KEY', 'clave-de-respaldo')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = ["*"]  # Permite acceso desde Codespaces o entornos compartidos

CSRF_TRUSTED_ORIGINS = [
    "https://*.app.github.dev",   # para tu Codespace
    "https://localhost:8000",     # para desarrollo local
    "http://localhost:8000",
    "https://crispy-space-halibut-wxx6rj4xpj9fgp4q.github.dev/",
]
# ============================================================
# APLICACIONES INSTALADAS
# ============================================================
INSTALLED_APPS = [
    # Apps de Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Tu aplicación principal
    'Incos_app',
]


# ============================================================
# MIDDLEWARE
# ============================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ============================================================
# CONFIGURACIÓN DE URLS Y WSGI
# ============================================================
ROOT_URLCONF = 'Incos.urls'
WSGI_APPLICATION = 'Incos.wsgi.application'


# ============================================================
# CONFIGURACIÓN DE TEMPLATES
# ============================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Carpeta global de plantillas
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# ============================================================
# BASE DE DATOS (Neon PostgreSQL)
# ============================================================
DATABASES = {
    'default': dj_database_url.parse(os.getenv("DATABASE_URL"))
}


# ============================================================
# VALIDACIÓN DE CONTRASEÑAS
# ============================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ============================================================
# INTERNACIONALIZACIÓN Y LOCALIZACIÓN
# ============================================================
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/La_Paz'
USE_I18N = True
USE_TZ = True

LOCALE_PATHS = [BASE_DIR / 'locale']


# ============================================================
# ARCHIVOS ESTÁTICOS (CSS, JS, IMÁGENES)
# ============================================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"


# ============================================================
# CONFIGURACIÓN DE MODELO DE USUARIO PERSONALIZADO
# ============================================================
AUTH_USER_MODEL = 'Incos_app.Usuario'


# ============================================================
# AUTENTICACIÓN Y REDIRECCIONES
# ============================================================
LOGIN_URL = '/'                 # Página de login
LOGIN_REDIRECT_URL = 'inicio'   # Redirección tras login exitoso
LOGOUT_REDIRECT_URL = '/'       # Redirección tras logout


# ============================================================
# CONFIGURACIÓN DE EMAIL (para recuperación de contraseñas)
# ============================================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')


# ============================================================
# CONFIGURACIÓN DE CLAVE PRIMARIA POR DEFECTO
# ============================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
