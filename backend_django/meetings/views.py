from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Sala, HorarioSala
from .serializer import SalaSerializer, SalaDetalleSerializer, HorarioSalaSerializer, HorarioSalaDetalleSerializer

class SalaViewSet(viewsets.ModelViewSet):
    queryset = Sala.objects.prefetch_related("horarios").all()
    permission_classes = [IsAuthenticated]
    serializer_class = SalaSerializer
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.action == "retrieve":
            return SalaDetalleSerializer
        return SalaSerializer

class HorarioSalaViewSet(viewsets.ModelViewSet):
    queryset = HorarioSala.objects.select_related('sala').all().order_by(
        "sala__nombre",
        "dia_semana",
        "hora_inicio"
    )
    serializer_class = HorarioSalaSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return HorarioSalaDetalleSerializer
        return HorarioSalaSerializer