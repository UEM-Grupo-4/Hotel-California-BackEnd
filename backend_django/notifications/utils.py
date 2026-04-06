from django.conf import settings
from django.core.mail import send_mail

from bookings.models import Reserva
from notifications.models import Notificacion

def enviar_email_reserva(reserva, mensaje):
    send_mail(
        subject="Actualización de tu reserva",
        message=mensaje,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[reserva.cliente.email],
        fail_silently=False,
    )

def crear_notificacion_reserva(reserva):
    if reserva.estado == Reserva.OpcionesEstado.CONFIRMADA:
        mensaje = f"Tu reserva con ID {reserva.id} ha sido confirmada."
    elif reserva.estado == Reserva.OpcionesEstado.RECHAZADA:
        mensaje = f"Tu reserva con ID {reserva.id} ha sido rechazada."
    elif reserva.estado == Reserva.OpcionesEstado.CANCELADA:
        mensaje = f"Tu reserva con ID {reserva.id} ha sido cancelada correctamente."
    elif reserva.estado == Reserva.OpcionesEstado.PENDIENTE:
        mensaje = (
            "Tu reserva ha sido registrada correctamente y está pendiente de validación.\n"
            f"Código de reserva: {reserva.code}\n"
            f"Consultar el estado de tu reserva aquí: http://localhost:5173/mi-reserva/?code={reserva.code}&email={reserva.cliente.email}"
        )     
    else:
        return None
    
    notificacion = Notificacion.objects.create(
        reserva=reserva,
        estado=Notificacion.OpcionesEstado.PENDIENTE,
        mensaje=mensaje,
    )
    
    try:
        enviar_email_reserva(reserva, mensaje)
        notificacion.estado = Notificacion.OpcionesEstado.ENVIADA
        notificacion.save(update_fields=["estado"])
    except Exception:
        notificacion.estado = Notificacion.OpcionesEstado.FALLIDA
        notificacion.save(update_fields=["estado"])
    
    return notificacion