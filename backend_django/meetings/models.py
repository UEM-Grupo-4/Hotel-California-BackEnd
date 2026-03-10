from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.

class Sala(models.Model):
    class OpcionesEstado(models.TextChoices):
        DISPONIBLE = "DISPONIBLE", "Disponible"
        MANTENIMIENTO = "MANTENIMIENTO", "Mantenimiento"
        FUERA_DE_SERVICIO = "FUERA_DE_SERVICIO", "Fuera de servicio"
    
    nombre = models.CharField(max_length=100, unique=True)
    capacidad = models.PositiveIntegerField()
    descripcion = models.CharField(max_length=255, blank=True)
    precio_hora = models.DecimalField(max_digits=8, decimal_places=2)
    estado = models.CharField(
        max_length=20,
        choices=OpcionesEstado.choices,
        default=OpcionesEstado.DISPONIBLE,
    )
    
    def __str__(self):
        return f"Sala: {self.nombre} || Capacidad: {self.capacidad} || Estado: {self.estado}"
    

class HorarioSala(models.Model):
    sala = models.ForeignKey(
        Sala,
        on_delete=models.CASCADE,
        related_name="horarios"
    )
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    
    def clean(self):
        if self.hora_fin <= self.hora_inicio:
            raise ValidationError("La hora final debe ser posterior a la hora de inicio.")
        
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["sala", "fecha", "hora_inicio", "hora_fin"],
                name="horario_sala_unico"
            )
        ]
        
    def __str__(self):
        return f"Sala: {self.sala} || Horario: {self.fecha} {self.hora_inicio}-{self.hora_fin}" 