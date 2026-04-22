from rest_framework import serializers
from .models import Sala, HorarioSala

class SalaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sala
        fields = ["id", "nombre", "capacidad", "descripcion", "image", "precio_hora", "estado"]
        
class HorarioSalaSerializer(serializers.ModelSerializer):
    nombre_sala = serializers.CharField(source="sala.nombre", read_only=True)
    
    class Meta:
        model = HorarioSala
        fields = ["id", "sala", "nombre_sala", "dia_semana", "hora_inicio", "hora_fin"]

    def validate(self, attrs):
        sala = attrs.get("sala", getattr(self.instance, "sala", None))
        dia_semana = attrs.get("dia_semana", getattr(self.instance, "dia_semana", None))        
        hora_inicio = attrs.get("hora_inicio", getattr(self.instance, "hora_inicio", None))
        hora_fin = attrs.get("hora_fin", getattr(self.instance, "hora_fin", None))

        if hora_fin <= hora_inicio:
            raise serializers.ValidationError(
                {"hora_fin": "La hora final debe ser posterior a la hora de inicio."}
            )

        # Evitar solapamientos en la misma sala y dia de semana
        conflicto = HorarioSala.objects.filter(
            sala=sala,
            dia_semana=dia_semana,
            hora_inicio__lt=hora_fin,
            hora_fin__gt=hora_inicio,
        )
        
        if self.instance:
            conflicto = conflicto.exclude(pk=self.instance.pk)
            
        if conflicto.exists():
            raise serializers.ValidationError(
                "El horario se solapa con otro existente para esta sala en ese día."
            )

        return attrs
        

class HorarioSalaDetalleSerializer(serializers.ModelSerializer):
    sala = SalaSerializer()
    
    class Meta:
        model = HorarioSala
        fields = ["id", "sala", "dia_semana", "hora_inicio", "hora_fin"]


class SalaDetalleSerializer(serializers.ModelSerializer):
    horarios = HorarioSalaDetalleSerializer(many=True, read_only=True)

    class Meta:
        model = Sala
        fields = [
            "id",
            "nombre",
            "capacidad",
            "descripcion",
            "precio_hora",
            "estado",
            "horarios",
        ]
        
