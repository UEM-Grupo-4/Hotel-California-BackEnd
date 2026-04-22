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
    image = models.ImageField(null=True, blank=True)
    precio_hora = models.DecimalField(max_digits=8, decimal_places=2)
    estado = models.CharField(
        max_length=20,
        choices=OpcionesEstado.choices,
        default=OpcionesEstado.DISPONIBLE,
    )
    
    def __str__(self):
        return f"Sala: {self.nombre} || Capacidad: {self.capacidad} || Estado: {self.estado}"
    

class HorarioSala(models.Model):
    class OpcionesDiaSemana(models.IntegerChoices):
        LUNES = 0, "Lunes"
        MARTES = 1, "Martes"
        MIERCOLES = 2, "Miercoles"
        JUEVES = 3, "Jueves"
        VIERNES = 4, "Viernes"
        SABADO = 5, "Sabado"
        DOMINGO = 6, "Domingo"

    sala = models.ForeignKey(
        Sala,
        on_delete=models.CASCADE,
        related_name="horarios"
    )
    dia_semana = models.PositiveSmallIntegerField(choices=OpcionesDiaSemana.choices)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    
    def clean(self):
        if self.hora_fin <= self.hora_inicio:
            raise ValidationError("La hora final debe ser posterior a la hora de inicio.")

        # Evitar solapamientos para la misma sala y dia de semana
        solapamiento = HorarioSala.objects.filter(
            sala=self.sala,
            dia_semana=self.dia_semana,
            hora_inicio__lt=self.hora_fin,
            hora_fin__gt=self.hora_inicio,
        ).exclude(pk=self.pk).exists()
        if solapamiento:
            raise ValidationError("El horario se solapa con otro existente para esta sala.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
        
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["sala", "dia_semana", "hora_inicio", "hora_fin"],
                name="horario_sala_unico"
            )
        ]

    def __str__(self):
        return f"Sala: {self.sala} || Horario: {self.get_dia_semana_display()} {self.hora_inicio}-{self.hora_fin}" 
