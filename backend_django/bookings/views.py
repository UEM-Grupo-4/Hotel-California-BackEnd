from rest_framework import mixins, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import OpenApiParameter, extend_schema

from rooms.models import Room
from rooms.serializer import RoomSerializer

from .models import Reserva, ReservaHabitacion, ReservaSala
from .serializer import (
    ReservaSerializer,
    CrearReservaHabitacionSerializer,
    CrearReservaSalaSerializer,
    DisponibilidadHabitacionesSerializer,
)


class ReservaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Reserva.objects.select_related("cliente").all().order_by("-fecha_creacion")
    serializer_class = ReservaSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"


class ReservaHabitacionViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = ReservaHabitacion.objects.select_related(
        "reserva",
        "habitacion",
        "habitacion__type",
        "reserva__cliente",
    ).all()
    serializer_class = CrearReservaHabitacionSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reserva_habitacion = serializer.save()
        reserva = reserva_habitacion.reserva
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reserva_sala = serializer.save()
        reserva = reserva_sala.reserva
        output = ReservaSerializer(reserva, context={"request": request}).data
        return Response(output, status=status.HTTP_201_CREATED)


class HabitacionesDisponiblesView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="fecha_inicio", required=True, type=str, location=OpenApiParameter.QUERY),
            OpenApiParameter(name="fecha_fin", required=True, type=str, location=OpenApiParameter.QUERY),
            OpenApiParameter(name="huespedes", required=True, type=int, location=OpenApiParameter.QUERY),
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
