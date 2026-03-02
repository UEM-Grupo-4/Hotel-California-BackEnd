from rest_framework import serializers
from .models import Habitacion, TipoHabitacion

class TipoHabitacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoHabitacion
        fields = ['id', 'tipo', 'capacidad', 'precio_noche']

class HabitacionSerializer(serializers.ModelSerializer):
    tipo = TipoHabitacionSerializer()

    class Meta:
        model = Habitacion
        fields = ['id', 'numero', 'descripcion', 'estado', 'tipo', 'creada_el', 'actualizada_el']
        read_only_fields = ['id', 'creada_el', 'actualizada_el']    

class HabitacionDetailSerializer(HabitacionSerializer):
    tipo = TipoHabitacionSerializer()

    class Meta(HabitacionSerializer.Meta):
        fields = HabitacionSerializer.Meta.fields + ['tipo']
        read_only_fields = HabitacionSerializer.Meta.read_only_fields + ['tipo']
        depth = 1
        
