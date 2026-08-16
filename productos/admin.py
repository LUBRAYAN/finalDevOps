from django.contrib import admin
from .models import Producto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'precio', 'activo', 'fecha_creacion']
    list_filter = ['activo', 'fecha_creacion']
    search_fields = ['codigo', 'nombre', 'descripcion']
    ordering = ['codigo']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']