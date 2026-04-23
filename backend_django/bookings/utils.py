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

        dia_semana = detalle.fecha.weekday()

        horario_valido = HorarioSala.objects.filter(
            sala=detalle.sala,
            dia_semana=dia_semana,
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

def rechazar_reservas_pendientes_solapadas(reserva_confirmada):
    reservas_rechazadas = []

    if reserva_confirmada.tipo_reserva == Reserva.OpcionesReserva.HABITACION:
        detalle = reserva_confirmada.reserva_habitacion

        conflictos = Reserva.objects.filter(
            tipo_reserva=Reserva.OpcionesReserva.HABITACION,
            estado=Reserva.OpcionesEstado.PENDIENTE,
            reserva_habitacion__habitacion=detalle.habitacion,
            reserva_habitacion__fecha_inicio__lt=detalle.fecha_fin,
            reserva_habitacion__fecha_fin__gt=detalle.fecha_inicio,
        ).exclude(pk=reserva_confirmada.pk)

    elif reserva_confirmada.tipo_reserva == Reserva.OpcionesReserva.SALA:
        detalle = reserva_confirmada.reserva_sala

        conflictos = Reserva.objects.filter(
            tipo_reserva=Reserva.OpcionesReserva.SALA,
            estado=Reserva.OpcionesEstado.PENDIENTE,
            reserva_sala__sala=detalle.sala,
            reserva_sala__fecha=detalle.fecha,
            reserva_sala__hora_inicio__lt=detalle.hora_fin,
            reserva_sala__hora_fin__gt=detalle.hora_inicio,
        ).exclude(pk=reserva_confirmada.pk)

    else:
        return reservas_rechazadas

    for reserva in conflictos:
        reserva.estado = Reserva.OpcionesEstado.RECHAZADA
        reserva.save(update_fields=["estado"])
        reservas_rechazadas.append(reserva)

    return reservas_rechazadas
