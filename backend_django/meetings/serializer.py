from rest_framework import serializers
from .models import Sala, HorarioSala

class SalaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sala
        fields = ["id", "nombre", "capacidad", "descripcion", "precio_hora", "estado"]
        
class HorarioSalaSerializer(serializers.ModelSerializer):
    class Meta:
        model = HorarioSala
        fields = ["id", "sala", "dia_semana", "hora_inicio", "hora_fin"]

    def validate(self, attrs):
        hora_inicio = attrs.get("hora_inicio")
        hora_fin = attrs.get("hora_fin")
        sala = attrs.get("sala")
        dia_semana = attrs.get("dia_semana")

        if hora_inicio and hora_fin and hora_fin <= hora_inicio:
            raise serializers.ValidationError(
                {"hora_fin": "La hora final debe ser posterior a la hora de inicio."}
            )

        # Evitar solapamientos en la misma sala y dia de semana
        if sala is not None and dia_semana is not None and hora_inicio and hora_fin:
            qs = HorarioSala.objects.filter(
                sala=sala,
                dia_semana=dia_semana,
                hora_inicio__lt=hora_fin,
                hora_fin__gt=hora_inicio,
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    {"sala": "El horario se solapa con otro existente para esta sala."}
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
        
