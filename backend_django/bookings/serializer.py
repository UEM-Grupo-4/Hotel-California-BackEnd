from django.db import transaction
from rest_framework import serializers
from bookings.models import Reserva, ReservaHabitacion, ReservaSala
from customers.models import Cliente, Telefono, telefono_validator
from rooms.models import Room
from meetings.models import Sala, HorarioSala
from datetime import datetime, timedelta


# Serializers para listar reservas
class ClienteResumenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ["id", "nombre", "apellido_1", "apellido_2", "email"]

class ReservaHabitacionDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservaHabitacion
        fields = ["habitacion", "fecha_inicio", "fecha_fin"]

class ReservaSalaDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservaSala
        fields = ["sala", "fecha", "hora_inicio", "hora_fin"]

class ReservaSerializer(serializers.ModelSerializer):
    cliente = ClienteResumenSerializer(read_only=True)
    reserva_habitacion = ReservaHabitacionDetalleSerializer(read_only=True)
    reserva_sala = ReservaSalaDetalleSerializer(read_only=True)

    class Meta:
        model = Reserva
        fields = [
            "id",
            "code",
            "fecha_creacion",
            "estado",
            "tipo_reserva",
            "observaciones",
            "cliente",
            "reserva_habitacion",
            "reserva_sala",
            ]

# Serializer para crear reserva base
class CrearReservaBaseSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=50)
    apellido_1 = serializers.CharField(max_length=100)
    apellido_2 = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True
    )
    email = serializers.EmailField()
    telefono = serializers.CharField(
        max_length=16,
         validators=[telefono_validator]
        )
    observaciones = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255
    )

    def obtener_o_crear_cliente(self, validated_data):
        nombre = validated_data.pop("nombre")
        apellido_1 = validated_data.pop("apellido_1")
        apellido_2 = validated_data.pop("apellido_2", "") # Ponemos una cadena vacia en caso de que no venga el segundo apelldo
        email = validated_data.pop("email")
        telefono = validated_data.pop("telefono")

        # Buscamos cliente por email y si no existe lo creamos con defaults
        cliente, _ = Cliente.objects.get_or_create(
            email=email,
            defaults={
                "nombre": nombre,
                "apellido_1": apellido_1,
                "apellido_2": apellido_2,
            }
        )
        # Buscamos el telefono, si existe no crea duplicado y si no, lo añade
        Telefono.objects.get_or_create(
            cliente=cliente,
            telefono=telefono
        )

        return cliente

    def crear_reserva_base(self, cliente, tipo_reserva, observaciones):
        return Reserva.objects.create(
            cliente=cliente,
            tipo_reserva=tipo_reserva,
            estado=Reserva.OpcionesEstado.PENDIENTE,
            observaciones=observaciones
        )

# Serializer para crear una reserva de habitación
class CrearReservaHabitacionSerializer(CrearReservaBaseSerializer):
    habitacion = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.all()
    )
    fecha_inicio = serializers.DateField(input_formats=["%d-%m-%Y", "%Y-%m-%d"])
    fecha_fin = serializers.DateField(input_formats=["%d-%m-%Y", "%Y-%m-%d"])

    def validate(self, attrs):
        if attrs["fecha_fin"] <= attrs["fecha_inicio"]:
            raise serializers.ValidationError(
                {"fecha_fin": "La fecha final debe ser posterior a la fecha de inicio."}
            )

        # Comprobamos si existe una reserva confirmada que se solape con la misma habitación
        solapamiento = ReservaHabitacion.objects.filter(
            habitacion=attrs["habitacion"],
            reserva__estado=Reserva.OpcionesEstado.CONFIRMADA,
            fecha_inicio__lt=attrs["fecha_fin"],
            fecha_fin__gt=attrs["fecha_inicio"],
        ).exists()

        if solapamiento:
            raise serializers.ValidationError(
                {"habitacion": "Habitación no disponible en las fechas seleccionadas."}
            )

        return attrs

    def create(self, validated_data):
        # Realizamos las operaciones dentro de una transacción para que no se guarden reservas parcialmente en caso de error
        with transaction.atomic():
            observaciones = validated_data.pop("observaciones", "")
            cliente = self.obtener_o_crear_cliente(validated_data)

            # Creamos la reserva general
            reserva = self.crear_reserva_base(
                cliente=cliente,
                tipo_reserva=Reserva.OpcionesReserva.HABITACION,
                observaciones=observaciones
            )

            # Creamos el detalle de la reserva de habitación
            reserva_habitacion = ReservaHabitacion.objects.create(
                reserva=reserva,
                habitacion=validated_data["habitacion"],
                fecha_inicio=validated_data["fecha_inicio"],
                fecha_fin=validated_data["fecha_fin"]
            )

            return reserva_habitacion


# Serializer para crear reserva de sala
class CrearReservaSalaSerializer(CrearReservaBaseSerializer):
    sala = serializers.PrimaryKeyRelatedField(
        queryset=Sala.objects.all()
    )
    fecha = serializers.DateField(input_formats=["%d-%m-%Y", "%Y-%m-%d"])
    hora_inicio = serializers.TimeField(input_formats=["%H:%M", "%H:%M:%S"])
    numero_horas = serializers.IntegerField(min_value=1)

    def validate(self, attrs):
        fecha = attrs["fecha"]
        hora_inicio = attrs["hora_inicio"]
        numero_horas = attrs["numero_horas"]

        # Solo permitir horas exactas: 10:00, 11:00, etc.
        if hora_inicio.minute != 0 or hora_inicio.second != 0:
            raise serializers.ValidationError(
                {"hora_inicio": "La hora de inicio debe ser una hora exacta, sin minutos ni segundos."}
            )

        # Calcular hora_fin a partir de hora_inicio + numero_horas
        dt_inicio = datetime.combine(fecha, hora_inicio)
        dt_fin = dt_inicio + timedelta(hours=numero_horas)
        hora_fin = dt_fin.time()

        attrs["hora_fin"] = hora_fin

        # Comprobar que la sala dispone del horario solicitado
        dia_semana = fecha.weekday()
        horario_valido = HorarioSala.objects.filter(
            sala=attrs["sala"],
            dia_semana=dia_semana,
            hora_inicio__lte=hora_inicio,
            hora_fin__gte=hora_fin,
        ).exists()

        if not horario_valido:
            raise serializers.ValidationError(
                {"sala": "Horario no disponible para esta sala."}
            )

        # Comprobar que no haya reserva confirmada solapada
        solapamiento = ReservaSala.objects.filter(
            sala=attrs["sala"],
            fecha=fecha,
            reserva__estado=Reserva.OpcionesEstado.CONFIRMADA,
            hora_inicio__lt=hora_fin,
            hora_fin__gt=hora_inicio,
        ).exists()

        if solapamiento:
            raise serializers.ValidationError(
                {"sala": "Sala no disponible en la fecha y horario seleccionados."}
            )

        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            observaciones = validated_data.pop("observaciones", "")
            cliente = self.obtener_o_crear_cliente(validated_data)

            reserva = self.crear_reserva_base(
                cliente=cliente,
                tipo_reserva=Reserva.OpcionesReserva.SALA,
                observaciones=observaciones
            )

            reserva_sala = ReservaSala.objects.create(
                reserva=reserva,
                sala=validated_data["sala"],
                fecha=validated_data["fecha"],
                hora_inicio=validated_data["hora_inicio"],
                hora_fin=validated_data["hora_fin"],
            )

            return reserva_sala

    def create(self, validated_data):
        with transaction.atomic():
            observaciones = validated_data.pop("observaciones", "")
            cliente = self.obtener_o_crear_cliente(validated_data)

            reserva = self.crear_reserva_base(
                cliente=cliente,
                tipo_reserva=Reserva.OpcionesReserva.SALA,
                observaciones=observaciones
            )

            reserva_sala = ReservaSala.objects.create(
                reserva=reserva,
                sala=validated_data["sala"],
                fecha=validated_data["fecha"],
                hora_inicio=validated_data["hora_inicio"],
                hora_fin=validated_data["hora_fin"],
            )

            return reserva_sala

# Serializer para ver la disponibilidad de las habitaciones
class DisponibilidadHabitacionesSerializer(serializers.Serializer):
    fecha_inicio = serializers.DateField(input_formats=["%d-%m-%Y", "%Y-%m-%d"])
    fecha_fin = serializers.DateField(input_formats=["%d-%m-%Y", "%Y-%m-%d"])
    huespedes = serializers.IntegerField(min_value=1)

    def validate(self, attrs):
        if attrs["fecha_fin"] <= attrs["fecha_inicio"]:
            raise serializers.ValidationError(
                {"fecha_fin": "La fecha final debe ser posterior a la fecha de inicio."}
            )
        return attrs
    
# Serializer para ver la disponibilidad de las habitaciones
from datetime import datetime, timedelta

class DisponibilidadSalasSerializer(serializers.Serializer):
    fecha = serializers.DateField(input_formats=["%d-%m-%Y", "%Y-%m-%d"])
    hora_inicio = serializers.TimeField(input_formats=["%H:%M", "%H:%M:%S"])
    numero_horas = serializers.IntegerField(min_value=1)
    personas = serializers.IntegerField(min_value=1)

    def validate(self, attrs):
        fecha = attrs["fecha"]
        hora_inicio = attrs["hora_inicio"]
        numero_horas = attrs["numero_horas"]

        # Solo permitir horas exactas
        if hora_inicio.minute != 0 or hora_inicio.second != 0:
            raise serializers.ValidationError(
                {"hora_inicio": "La hora de inicio debe ser una hora exacta, sin minutos ni segundos."}
            )

        # Calcular hora_fin automáticamente
        dt_inicio = datetime.combine(fecha, hora_inicio)
        dt_fin = dt_inicio + timedelta(hours=numero_horas)
        attrs["hora_fin"] = dt_fin.time()

        return attrs
    
# Serializer para cancelar una reserva (clientes)
class CancelarReservaSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)
    email = serializers.EmailField()

# Serializer para el Response de Swagger
class CancelarReservaResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()
    reserva = ReservaSerializer()
