from bookings.models import ReservaHabitacion, ReservaSala, Reserva
from meetings.models import HorarioSala

def reserva_puede_confirmarse(reserva):
    if reserva.tipo_reserva == Reserva.OpcionesReserva.HABITACION:
        detalle = reserva.reserva_habitacion
        
        conflicto = ReservaHabitacion.objects.filter(
            habitacion=detalle.habitacion,
            reserva__estado=Reserva.OpcionesEstado.CONFIRMADA,
            fecha_inicio__lt=detalle.fecha_fin,
            fecha_fin__gt=detalle.fecha_inicio,
        ).exclude(reserva=reserva).exists()
        
        return not conflicto

    if reserva.tipo_reserva == Reserva.OpcionesReserva.SALA:
        detalle = reserva.reserva_sala
        
        horario_valido = HorarioSala.objects.filter(
            sala=detalle.sala,
            fecha=detalle.fecha,
            hora_inicio__lte=detalle.hora_inicio,
            hora_fin__gte=detalle.hora_fin,
        ).exists()
        
        if not horario_valido:
            return False
        
        conflicto = ReservaSala.objects.filter(
            sala=detalle.sala,
            fecha=detalle.fecha,
            reserva__estado=Reserva.OpcionesEstado.CONFIRMADA,
            hora_inicio__lt=detalle.hora_fin,
            hora_fin__gt=detalle.hora_inicio,
        ).exclude(reserva=reserva).exists()
        
        return not conflicto
    return False