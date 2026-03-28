from django.db import models

# Create your models here.


class Notificacion(models.Model):
    class OpcionesCanal(models.TextChoices):
         EMAIL = 'EMAIL', 'Email'
         SMS = 'SMS', 'SMS'
         WHATSAPP = "WHATSAPP", 'WhatsApp'

    class OpcionesEstado(models.TextChoices):
         PENDIENTE = 'PENDIENTE', 'Pendiente'
         ENVIADA = 'ENVIADA', 'Enviada'
         FALLIDA = "FALLIDA", 'Fallida'      
         
    canal = models.CharField(
        max_length=12,
        choices=OpcionesCanal.choices,
        default=OpcionesCanal.EMAIL        
    )    
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=10,
        choices=OpcionesEstado.choices,
        default=OpcionesEstado.PENDIENTE
    )
    reserva = models.ForeignKey("bookings.Reserva", on_delete=models.CASCADE, related_name="notificaciones")
    
    def __str__(self):
        return f"Notificación: {self.id} | Canal: {self.canal} | Estado: {self.estado} | Reserva: {self.reserva_id}"
    