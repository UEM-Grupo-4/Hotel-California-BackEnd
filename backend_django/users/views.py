from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import User
from .serializer import UserSerializer

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'
    permission_classes = [AllowAny]

    

