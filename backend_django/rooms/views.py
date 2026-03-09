from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Room, RoomType, Amenity
from .serializer import RoomSerializer, RoomTypeSerializer, AmenitySerializer

class RoomViewSet(viewsets.ModelViewSet):

    queryset = Room.objects.select_related('type').all()

    serializer_class = RoomSerializer

    permission_classes = [IsAuthenticatedOrReadOnly]

    lookup_field = 'id'


class RoomTypeViewSet(viewsets.ModelViewSet):

    queryset = RoomType.objects.all()

    serializer_class = RoomTypeSerializer

    permission_classes = [IsAuthenticatedOrReadOnly]

    lookup_field = 'id'

class AmenityViewSet(viewsets.ModelViewSet):

    queryset = Amenity.objects.all()

    serializer_class = AmenitySerializer

    permission_classes = [IsAuthenticatedOrReadOnly]

    lookup_field = "id"
