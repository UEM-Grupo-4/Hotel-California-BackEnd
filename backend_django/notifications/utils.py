from bookings.models import Reserva
from notifications.models import Notificacion

def crear_notificacion_reserva(reserva):
    if reserva.estado == Reserva.OpcionesEstado.CONFIRMADA:
        mensaje = f"Tu reserva con ID {reserva.id} ha sido confirmada."
    elif reserva.estado == Reserva.OpcionesEstado.RECHAZADA:
        mensaje = f"Tu reserva con ID {reserva.id} ha sido rechazada."
        
    else:
        return None
    
    notificacion = Notificacion.objects.create(
        reserva=reserva,
        estado=Notificacion.OpcionesEstado.PENDIENTE,
        mensaje=mensaje,
    )
    
    return notificacion