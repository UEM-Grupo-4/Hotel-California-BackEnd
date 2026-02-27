from rest_framework import serializers
from .models import Cliente, Telefono

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['id', 'nombre', 'apellido_1', 'apellido_2', 'email']
        read_only_fields = ['id']

class TelefonoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Telefono
        fields = ['id', 'cliente', 'telefono']
        read_only_fields = ['id']

class ClienteDetailSerializer(ClienteSerializer):
    telefonos = TelefonoSerializer(many=True, read_only=True)

    class Meta(ClienteSerializer.Meta):
        fields = ClienteSerializer.Meta.fields + ['telefonos']

class TelefonoDetailSerializer(TelefonoSerializer):
    cliente = ClienteSerializer(read_only=True)

    class Meta(TelefonoSerializer.Meta):
        fields = TelefonoSerializer.Meta.fields + ['cliente']

    