# C:\Incos\Incos\urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # CORRECCIÓN: Usar 'Incos_app' para que coincida con el nombre de tu carpeta/módulo.
    path('', include('Incos_app.urls')),
]