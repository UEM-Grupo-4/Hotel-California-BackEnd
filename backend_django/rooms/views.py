from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Habitacion, TipoHabitacion
from .serializer import HabitacionSerializer, TipoHabitacionSerializer

# Create your views here.
class HabitacionViewSet(viewsets.ModelViewSet):
    queryset = Habitacion.objects.select_related('tipo').all()
    permission_classes = [AllowAny]
    serializer_class = HabitacionSerializer
    lookup_field = 'id'

class TipoHabitacionViewSet(viewsets.ModelViewSet):
    queryset = TipoHabitacion.objects.all()
    permission_classes = [AllowAny]
    serializer_class = TipoHabitacionSerializer
    lookup_field = 'id'


