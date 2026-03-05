from django.db import models

# Create your models here.
class Habitacion(models.Model):
    ESTADOS = [
        ("available", "Disponible"),
        ("occupied", "Ocupada"),
        ("maintenance", "Mantenimiento"),
    ]

    numero = models.CharField(max_length=10, unique=True, help_text="Número o código de la habitación")
    descripcion = models.CharField(max_length=200, blank=True, help_text="Descripción opcional de la habitación")
    estado = models.CharField(max_length=12, choices=ESTADOS, default="available")
    tipo = models.ForeignKey("TipoHabitacion", on_delete=models.CASCADE)
    creada_el = models.DateTimeField(auto_now_add=True)
    actualizada_el = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Habitación {self.numero} ({self.get_estado_display()}) - {self.tipo.tipo}"

class TipoHabitacion(models.Model):
    tipo = models.CharField(max_length=50, help_text="Ej. Ocean view, Estándar, Suite")
    capacidad = models.PositiveSmallIntegerField(help_text="Número máximo de personas")
    precio_noche = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.tipo} (capacidad {self.capacidad}) - ${self.precio_noche}/noche"
