from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .models import Cliente, Telefono
from .serializer import (
    ClienteDetailSerializer,
    ClienteSerializer,
    TelefonoDetailSerializer,
    TelefonoSerializer,
)


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    permission_classes = [AllowAny]
    serializer_class = ClienteSerializer
    lookup_field = 'id'
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ClienteDetailSerializer
        return ClienteSerializer


class TelefonoViewSet(viewsets.ModelViewSet):
    queryset = Telefono.objects.select_related('cliente').all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TelefonoDetailSerializer
        return TelefonoSerializer
