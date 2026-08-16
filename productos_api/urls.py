from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # IMPORTANTE: Incluye las URLs de la app productos
    path('api/', include('productos.urls')),  # Esto es lo que falta
]