from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

class Producto(models.Model):
    codigo = models.CharField(
        max_length=50, 
        unique=True, 
        db_index=True,
        verbose_name="Código"
    )
    nombre = models.CharField(
        max_length=200, 
        db_index=True,
        verbose_name="Nombre"
    )
    descripcion = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Descripción"
    )
    precio = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Precio"
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de actualización"
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        indexes = [
            models.Index(fields=['codigo', 'nombre']),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    def save(self, *args, **kwargs):
        self.codigo = self.codigo.strip().upper()
        self.nombre = self.nombre.strip().title()
        if self.descripcion:
            self.descripcion = self.descripcion.strip()
        super().save(*args, **kwargs)