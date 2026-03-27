from django.db import transaction
from rest_framework import serializers
from bookings.models import Reserva, ReservaHabitacion, ReservaSala
from customers.models import Cliente, Telefono, telefono_validator
from rooms.models import Room
from meetings.models import Sala, HorarioSala


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
    fecha_inicio = serializers.DateField()
    fecha_fin = serializers.DateField()

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
    fecha = serializers.DateField()
    hora_inicio = serializers.TimeField()
    hora_fin = serializers.TimeField()

    def validate(self, attrs):
        if attrs["hora_fin"] <= attrs["hora_inicio"]:
            raise serializers.ValidationError(
                {"hora_fin": "La hora final debe ser posterior a la hora de inicio."}
            )

        # Comprobamos que la sala dispone del horario solicitado (recurrente por dia de semana)
        dia_semana = attrs["fecha"].weekday()
        horario_valido = HorarioSala.objects.filter(
            sala=attrs["sala"],
            dia_semana=dia_semana,
            hora_inicio__lte=attrs["hora_inicio"],
            hora_fin__gte=attrs["hora_fin"],
        ).exists()

        if not horario_valido:
            raise serializers.ValidationError(
                {"sala": "Horario no disponible para esta sala"}
            )

        # Confirmamos que no exista ninguna reserva confirmada que se solape
        solapamiento = ReservaSala.objects.filter(
            sala=attrs["sala"],
            fecha=attrs["fecha"],
            reserva__estado=Reserva.OpcionesEstado.CONFIRMADA,
            hora_inicio__lt=attrs["hora_fin"],
            hora_fin__gt=attrs["hora_inicio"],
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
                hora_fin=validated_data["hora_fin"]
            )

            return reserva_sala


class DisponibilidadHabitacionesSerializer(serializers.Serializer):
    fecha_inicio = serializers.DateField()
    fecha_fin = serializers.DateField()
    huespedes = serializers.IntegerField(min_value=1)

    def validate(self, attrs):
        if attrs["fecha_fin"] <= attrs["fecha_inicio"]:
            raise serializers.ValidationError(
                {"fecha_fin": "La fecha final debe ser posterior a la fecha de inicio."}
            )
        return attrs
