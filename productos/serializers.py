from rest_framework import serializers
from .models import Producto

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = [
            'id', 
            'codigo', 
            'nombre', 
            'descripcion', 
            'precio',
            'fecha_creacion',
            'fecha_actualizacion',
            'activo'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']

    def validate_codigo(self, value):
        """Validar que el código no tenga espacios y esté en mayúsculas"""
        value = value.strip().upper()
        if not value:
            raise serializers.ValidationError("El código no puede estar vacío")
        return value

    def validate_precio(self, value):
        """Validar que el precio sea positivo"""
        if value < 0:
            raise serializers.ValidationError("El precio debe ser mayor o igual a 0")
        return value

    def validate_nombre(self, value):
        """Validar nombre no vacío"""
        value = value.strip()
        if not value:
            raise serializers.ValidationError("El nombre no puede estar vacío")
        return value

class ProductoListSerializer(serializers.ModelSerializer):
    """Serializer para listar productos con menos campos"""
    class Meta:
        model = Producto
        fields = ['id', 'codigo', 'nombre', 'precio']