from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .models import Sala, HorarioSala
from .serializer import SalaSerializer, HorarioSalaSerializer, HorarioSalaDetalleSerializer

class SalaViewSet(viewsets.ModelViewSet):
    queryset = Sala.objects.all()
    permission_classes = [AllowAny]
    serializer_class = SalaSerializer
    lookup_field = 'id'

class HorarioSalaViewSet(viewsets.ModelViewSet):
    queryset = HorarioSala.objects.select_related('sala').all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return HorarioSalaDetalleSerializer
        return HorarioSalaSerializer
    

# Create your views here.
