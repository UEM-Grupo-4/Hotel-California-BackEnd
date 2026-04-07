from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, OpenApiExample, extend_schema

from .utils import reserva_puede_confirmarse

from .serializer import DisponibilidadSalasSerializer

from notifications.utils import crear_notificacion_reserva

from rooms.models import Room
from rooms.serializer import RoomSerializer

from meetings.models import Sala, HorarioSala
from meetings.serializer import SalaSerializer

from .models import Reserva, ReservaHabitacion, ReservaSala
from .serializer import (
    ReservaSerializer,
    CrearReservaHabitacionSerializer,
    CrearReservaSalaSerializer,
    DisponibilidadHabitacionesSerializer,
    CancelarReservaSerializer,
    CancelarReservaResponseSerializer
)


class ReservaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Reserva.objects.select_related(
        "cliente",
        "reserva_habitacion",
        "reserva_sala",
    ).all().order_by("-fecha_creacion")
    serializer_class = ReservaSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    
    @extend_schema(
        request=None,
        responses={
            200: {
                "type": "object",
                "properties":{
                    "detail":{"type": "string"}
                }
            }
        }
    )
    @action(detail=True, methods=["post"])
    def confirmar(self, request, id=None):
        reserva = self.get_object()
        
        if reserva.estado == Reserva.OpcionesEstado.CONFIRMADA:
            return Response(
                {"detail": "La reserva ya está confirmada."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if reserva.estado == Reserva.OpcionesEstado.CANCELADA:
            return Response(
                {"detail": "No se puede confirmar una reserva cancelada."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if not reserva_puede_confirmarse(reserva):
            return Response(
                {"detail": "La reserva no puede confirmarse porque ya no hay disponibilidad."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        reserva.estado = Reserva.OpcionesEstado.CONFIRMADA
        reserva.save()
        
        crear_notificacion_reserva(reserva)
        
        return Response(
            {"detail": "Reserva confirmada correctamente."},
            status=status.HTTP_200_OK
        )
        
    @extend_schema(
        request=None,
        responses={
            200: {
                "type": "object",
                "properties":{
                    "detail":{"type": "string"}
                }
            }
        }
    )
    @action(detail=True, methods=["post"])
    def rechazar(self, request, id=None):
        reserva = self.get_object()
        
        if reserva.estado == Reserva.OpcionesEstado.RECHAZADA:
            return Response(
                {"detail": "La reserva ya está rechazada."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if reserva.estado == Reserva.OpcionesEstado.CANCELADA:
            return Response(
                {"detail": "No se puede rechazar una reserva cancelada."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        reserva.estado = Reserva.OpcionesEstado.RECHAZADA
        reserva.save()
        
        crear_notificacion_reserva(reserva)
        
        return Response(
            {"detail": "Reserva rechazada correctamente."},
            status=status.HTTP_200_OK
        )


class ReservaHabitacionViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = ReservaHabitacion.objects.select_related(
        "reserva",
        "habitacion",
        "habitacion__type",
        "reserva__cliente",
    ).all()
    serializer_class = CrearReservaHabitacionSerializer
    permission_classes = [AllowAny]
    
    @extend_schema(
        examples=[
            OpenApiExample(
                "Ejemplo reserva habitación",
                value={
                    "nombre": "string",
                    "apellido_1": "string",
                    "email": "user@example.com",
                    "telefono": "+989127889099",
                    "habitacion": 1,
                    "fecha_inicio": "06-04-2026",
                    "fecha_fin": "09-04-2026"
                },
                request_only=True,
            )
        ]
    )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reserva_habitacion = serializer.save()
        reserva = reserva_habitacion.reserva
        
        crear_notificacion_reserva(reserva)
        
        output = ReservaSerializer(reserva, context={"request": request}).data
        return Response(output, status=status.HTTP_201_CREATED)


class ReservaSalaViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = ReservaSala.objects.select_related(
        "reserva",
        "sala",
        "reserva__cliente",
    ).all()
    serializer_class = CrearReservaSalaSerializer
    permission_classes = [AllowAny]
    
    @extend_schema(
        examples=[
            OpenApiExample(
                "Ejemplo reserva sala",
                value={
                    "nombre": "string",
                    "apellido_1": "string",
                    "email": "user@example.com",
                    "telefono": "+34600111222",
                    "sala": 1,
                    "fecha": "15-04-2026",
                    "hora_inicio": "10:00",
                    "numero_horas": 2
                },
                request_only=True,
            )
        ]
    )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reserva_sala = serializer.save()
        reserva = reserva_sala.reserva
        
        crear_notificacion_reserva(reserva)
        
        output = ReservaSerializer(reserva, context={"request": request}).data
        return Response(output, status=status.HTTP_201_CREATED)


class HabitacionesDisponiblesView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="fecha_inicio", required=True, type=str, location=OpenApiParameter.QUERY, description="Fecha de inicio"),
            OpenApiParameter(name="fecha_fin", required=True, type=str, location=OpenApiParameter.QUERY, description="Fecha fin"),
            OpenApiParameter(name="huespedes", required=True, type=int, location=OpenApiParameter.QUERY, description="Huespedes"),
        ],
        responses={200: RoomSerializer(many=True)},
    )
    def get(self, request):
        query = DisponibilidadHabitacionesSerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        data = query.validated_data

        fecha_inicio = data["fecha_inicio"]
        fecha_fin = data["fecha_fin"]
        huespedes = data["huespedes"]

        rooms_qs = Room.objects.select_related("type").filter(type__capacity__gte=huespedes)

        ocupadas_ids = ReservaHabitacion.objects.filter(
            reserva__estado=Reserva.OpcionesEstado.CONFIRMADA,
            fecha_inicio__lt=fecha_fin,
            fecha_fin__gt=fecha_inicio,
        ).values_list("habitacion_id", flat=True)

        disponibles = rooms_qs.exclude(id__in=ocupadas_ids)
        serializer = RoomSerializer(disponibles, many=True, context={"request": request})
        return Response(serializer.data)
    
class SalasDisponiblesView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="fecha",
                required=True,
                type=str,
                location=OpenApiParameter.QUERY,
                description="Fecha en formato DD-MM-YYYY o YYYY-MM-DD"
            ),
            OpenApiParameter(
                name="numero_horas",
                required=True,
                type=int,
                location=OpenApiParameter.QUERY,
                description="Número de horas completas"
            ),
            OpenApiParameter(
                name="personas",
                required=True,
                type=int,
                location=OpenApiParameter.QUERY,
                description="Número de personas"
            ),
        ],
        responses={200: SalaSerializer(many=True)},
    )
    def get(self, request):
        query = DisponibilidadSalasSerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        data = query.validated_data

        fecha = data["fecha"]
        hora_inicio = data["hora_inicio"]
        hora_fin = data["hora_fin"]
        personas = data["personas"]

        dia_semana = fecha.weekday()

        salas_qs = Sala.objects.filter(
            capacidad__gte=personas,
            estado=Sala.OpcionesEstado.DISPONIBLE,
        )

        salas_con_horario = HorarioSala.objects.filter(
            dia_semana=dia_semana,
            hora_inicio__lte=hora_inicio,
            hora_fin__gte=hora_fin,
        ).values_list("sala_id", flat=True)

        salas_ocupadas = ReservaSala.objects.filter(
            fecha=fecha,
            reserva__estado=Reserva.OpcionesEstado.CONFIRMADA,
            hora_inicio__lt=hora_fin,
            hora_fin__gt=hora_inicio,
        ).values_list("sala_id", flat=True)

        disponibles = salas_qs.filter(
            id__in=salas_con_horario
        ).exclude(
            id__in=salas_ocupadas
        )

        serializer = SalaSerializer(disponibles, many=True, context={"request": request})
        return Response(serializer.data)

class ReservaSearchView(APIView):
    permission_classes = [AllowAny]
    
    def get_reserva(self, code, email):
        try:
            return Reserva.objects.select_related("cliente").get(
                code=code,
                cliente__email=email,
            )
        except Reserva.DoesNotExist:
            return None     
        
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="code",
                required=True,
                type=str,
                location=OpenApiParameter.QUERY,
                description="Código de la reserva"
            ),
            OpenApiParameter(
                name="email",
                required=True,
                type=str,
                location=OpenApiParameter.QUERY,
                description="Email del cliente asociado a la reserva"
            ),
        ],
        responses={
            200: ReservaSerializer,
            400: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        }
    )  
    def get(self, request):
        code = request.query_params.get("code")
        email = request.query_params.get("email")

        if not code or not email:
            return Response(
                {"detail": "Los campos code e email son obligatorios."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reserva = self.get_reserva(code, email)
        
        if not reserva:
            return Response(
                {"detail": "Reserva no encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            ) 

        serializer = ReservaSerializer(reserva, context={"request": request})
        return Response(serializer.data)
    
    @extend_schema(
        request=CancelarReservaSerializer,
        responses={
            200: CancelarReservaResponseSerializer,
            400: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        }
    )
    def post(self, request):
        code = request.data.get("code")
        email = request.data.get("email")
        
        if not code or not email:
            return Response(
                {"detail": "Los campos code e email son obligatorios."},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        reserva = self.get_reserva(code, email)
        
        if not reserva:
            return Response(
                {"detail": "Reserva no encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )
            
        if reserva.estado == Reserva.OpcionesEstado.CANCELADA:
            return Response(
                {"detail": "La reserva ya está cancelada."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if reserva.estado == Reserva.OpcionesEstado.RECHAZADA:
            return Response(
                {"detail": "No se puede cancelar una reserva rechazada."},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        reserva.estado = Reserva.OpcionesEstado.CANCELADA
        reserva.save()
        
        crear_notificacion_reserva(reserva)

        serializer = ReservaSerializer(reserva, context={"request": request})
        return Response(
            {
                "detail": "Reserva cancelada correctamente.",
                "reserva": serializer.data
            },
            status=status.HTTP_200_OK,
        )
        
        