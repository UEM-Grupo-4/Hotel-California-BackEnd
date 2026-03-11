from rest_framework import serializers
from .models import Sala, HorarioSala

class SalaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sala
        fields = ["id", "nombre", "capacidad", "descripcion", "precio_hora", "estado"]
        
class HorarioSalaSerializer(serializers.ModelSerializer):
    class Meta:
        model = HorarioSala
        fields = ["id", "sala", "fecha", "hora_inicio", "hora_fin"]
        

class HorarioSalaDetalleSerializer(serializers.ModelSerializer):
    sala = SalaSerializer()
    
    class Meta:
        model = HorarioSala
        fields = ["id", "sala", "fecha", "hora_inicio", "hora_fin"]
        