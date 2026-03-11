from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.

class Reserva(models.Model):
    class OpcionesEstado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        CONFIRMADA = "CONFIRMADA", "Confirmada"
        RECHAZADA = "RECHAZADA", "Rechazada"
        CANCELADA = "CANCELADA", "Cancelada"

    class OpcionesReserva(models.TextChoices):
        HABITACION = "HABITACION", "Habitación"
        SALA = "SALA", "Sala"

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=12,
        choices=OpcionesEstado.choices,
        default=OpcionesEstado.PENDIENTE
    )
    tipo_reserva = models.CharField(
        max_length=10,
        choices=OpcionesReserva.choices
    )
    observaciones = models.CharField(max_length=255, blank=True)
    cliente = models.ForeignKey("customers.Cliente", on_delete=models.PROTECT, related_name='reservas') # PONEMOS PROTECT PARA NO BORRAR EL HISTÓRICO DE RESERVAS

    def __str__(self):
        return f"Reserva: {self.id} || Cliente: {self.cliente} || Tipo de reserva : {self.tipo_reserva} ||  Estado: {self.estado}"

class ReservaHabitacion(models.Model):
    reserva = models.OneToOneField(Reserva, on_delete=models.PROTECT, related_name="reserva_habitacion")
    habitacion = models.ForeignKey("rooms.Room", on_delete=models.PROTECT, related_name="reservas_habitacion")
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    def clean(self):
        if self.fecha_fin <= self.fecha_inicio:
            raise ValidationError("La fecha_fin debe ser posterior a la fecha_inicio.")
        if self.reserva.tipo_reserva != Reserva.OpcionesReserva.HABITACION:
            raise ValidationError("La reserva asociada debe ser de tipo HABITACION.")

    def __str__(self):
        return f"Reserva habitación {self.habitacion} ({self.fecha_inicio} - {self.fecha_fin})"

class ReservaSala(models.Model):
    reserva = models.OneToOneField(Reserva, on_delete=models.PROTECT, related_name="reserva_sala")
    sala = models.ForeignKey("meetings.Sala", on_delete=models.PROTECT, related_name="reservas_sala", null=True, blank=True)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def clean(self):
        if self.hora_fin <= self.hora_inicio:
            raise ValidationError("La hora_fin debe ser posterior a la hora_inicio.")
        if self.reserva.tipo_reserva != Reserva.OpcionesReserva.SALA:
            raise ValidationError("La reserva asociada debe ser de tipo SALA.")

        # Evitar solapamientos con reservas confirmadas
        if self.reserva.estado == Reserva.OpcionesEstado.CONFIRMADA:
            solapamiento = ReservaSala.objects.filter(
                sala=self.sala,
                fecha=self.fecha,
                reserva__estado=Reserva.OpcionesEstado.CONFIRMADA,
                hora_inicio__lt=self.hora_fin,
                hora_fin__gt=self.hora_inicio,
            ).exclude(pk=self.pk).exists()
            if solapamiento:
                raise ValidationError("Sala no disponible en la fecha y horario seleccionados.")

    def __str__(self):
        return f"Reserva sala: {self.sala} ({self.fecha} {self.hora_inicio}-{self.hora_fin})"

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
