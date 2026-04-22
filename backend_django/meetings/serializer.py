import json

from rest_framework import serializers
from .models import Sala, HorarioSala


# Serializer para listas de horarios
# Sirve cuando en el POST /meetings/horarios/ mandamos varios horarios de golpe
class HorarioSalaListSerializer(serializers.ListSerializer):
    def validate(self, data):
        # Validar solapamientos entre los propios horarios enviados
        # en la misma petición, no solo contra la base de datos.
        for i, item_1 in enumerate(data):
            for j, item_2 in enumerate(data):
                # Evitar comparaciones duplicadas y consigo mismo
                if i >= j:
                    continue

                # Solo tiene sentido comprobar solapamientos
                # si pertenecen a la misma sala y al mismo día.
                misma_sala_y_dia = (
                    item_1["sala"] == item_2["sala"]
                    and item_1["dia_semana"] == item_2["dia_semana"]
                )

                if not misma_sala_y_dia:
                    continue

                # Hay solapamiento si el inicio de uno es menor que el fin del otro
                # y el fin de uno es mayor que el inicio del otro.
                se_solapan = (
                    item_1["hora_inicio"] < item_2["hora_fin"]
                    and item_1["hora_fin"] > item_2["hora_inicio"]
                )

                if se_solapan:
                    raise serializers.ValidationError(
                        f"Los horarios en las posiciones {i} y {j} se solapan entre sí."
                    )

        return data

    def create(self, validated_data):
        # Crear todos los horarios de golpe
        horarios = [HorarioSala(**item) for item in validated_data]
        return HorarioSala.objects.bulk_create(horarios)


class HorarioSalaSerializer(serializers.ModelSerializer):
    # Campo extra de solo lectura para mostrar el nombre de la sala
    # sin tener que hacer otra petición desde frontend.
    nombre_sala = serializers.CharField(source="sala.nombre", read_only=True)

    class Meta:
        model = HorarioSala
        fields = ["id", "sala", "nombre_sala", "dia_semana", "hora_inicio", "hora_fin"]

        # Cuando el serializer se use con many=True,
        # utilizará este ListSerializer personalizado.
        list_serializer_class = HorarioSalaListSerializer

    def validate(self, attrs):
        # Si estamos creando, attrs trae todos los campos.
        # Si estamos editando, puede que no vengan todos,
        # así que usamos getattr(self.instance, ...) como respaldo.
        sala = attrs.get("sala", getattr(self.instance, "sala", None))
        dia_semana = attrs.get("dia_semana", getattr(self.instance, "dia_semana", None))
        hora_inicio = attrs.get("hora_inicio", getattr(self.instance, "hora_inicio", None))
        hora_fin = attrs.get("hora_fin", getattr(self.instance, "hora_fin", None))

        # Validar que la hora final sea posterior a la inicial
        if hora_fin <= hora_inicio:
            raise serializers.ValidationError(
                {"hora_fin": "La hora final debe ser posterior a la hora de inicio."}
            )

        # Evitar solapamientos en la misma sala y día de semana
        conflicto = HorarioSala.objects.filter(
            sala=sala,
            dia_semana=dia_semana,
            hora_inicio__lt=hora_fin,
            hora_fin__gt=hora_inicio,
        )

        # Si estamos editando, excluir el propio registro
        # para que no choque consigo mismo.
        if self.instance:
            conflicto = conflicto.exclude(pk=self.instance.pk)

        if conflicto.exists():
            raise serializers.ValidationError(
                "El horario se solapa con otro existente para esta sala en ese día."
            )

        return attrs


class SalaSerializer(serializers.ModelSerializer):
    # Para entrada usamos JSONField, porque con FormData el frontend manda
    # "horarios" como string JSON. Así evitamos problemas con nested serializers
    # + multipart/form-data.
    horarios = serializers.JSONField(required=False)

    class Meta:
        model = Sala
        fields = [
            "id",
            "nombre",
            "capacidad",
            "descripcion",
            "image",
            "precio_hora",
            "estado",
            "horarios",
        ]

    def to_internal_value(self, data):
        # Si la request viene como multipart/form-data,
        # "horarios" suele llegar como string JSON.
        #
        # Ejemplo:
        # '[{"dia_semana":0,"hora_inicio":"10:00:00","hora_fin":"16:00:00"}]'
        #
        # Aquí lo convertimos manualmente a lista Python.
        data = data.copy()

        horarios = data.get("horarios")

        if isinstance(horarios, str):
            try:
                data["horarios"] = json.loads(horarios)
            except json.JSONDecodeError:
                raise serializers.ValidationError(
                    {"horarios": "El campo horarios debe ser un JSON válido."}
                )

        return super().to_internal_value(data)

    def validate_horarios(self, horarios):
        # El campo debe ser una lista
        if not isinstance(horarios, list):
            raise serializers.ValidationError("El campo horarios debe ser una lista.")

        for index, horario in enumerate(horarios):
            # Cada elemento debe ser un objeto/dict
            if not isinstance(horario, dict):
                raise serializers.ValidationError(
                    f"El horario en la posición {index} debe ser un objeto."
                )

            # Comprobar campos obligatorios
            required_fields = {"dia_semana", "hora_inicio", "hora_fin"}
            missing = required_fields - set(horario.keys())

            if missing:
                raise serializers.ValidationError(
                    f"Faltan campos en el horario de la posición {index}: {', '.join(sorted(missing))}."
                )

            # Validar que dia_semana esté entre 0 y 6
            dia_semana = horario["dia_semana"]
            if dia_semana not in [0, 1, 2, 3, 4, 5, 6]:
                raise serializers.ValidationError(
                    f"El dia_semana del horario en la posición {index} debe estar entre 0 y 6."
                )

            # Validar formato y coherencia usando el serializer de horario anidado
            nested_serializer = HorarioSalaSerializer(
                data={
                    "sala": 1,  # valor ficticio solo para reutilizar parte de la validación estructural
                    "dia_semana": horario["dia_semana"],
                    "hora_inicio": horario["hora_inicio"],
                    "hora_fin": horario["hora_fin"],
                }
            )

            # Ojo: no llamamos a is_valid() porque intentaría validar la sala
            # contra BD. Validamos horas manualmente abajo.
            if horario["hora_fin"] <= horario["hora_inicio"]:
                raise serializers.ValidationError(
                    f"La hora final debe ser posterior a la inicial en el horario de la posición {index}."
                )

        # Validar solapamientos entre horarios enviados
        # dentro de la propia sala en la misma petición.
        for i, item_1 in enumerate(horarios):
            for j, item_2 in enumerate(horarios):
                # Evitar comparaciones duplicadas y consigo mismo
                if i >= j:
                    continue

                # Solo comparamos si es el mismo día
                if item_1["dia_semana"] != item_2["dia_semana"]:
                    continue

                se_solapan = (
                    item_1["hora_inicio"] < item_2["hora_fin"]
                    and item_1["hora_fin"] > item_2["hora_inicio"]
                )

                if se_solapan:
                    raise serializers.ValidationError(
                        f"Los horarios en las posiciones {i} y {j} se solapan entre sí."
                    )

        return horarios

    def create(self, validated_data):
        # Sacar horarios antes de crear la sala,
        # porque no son campos directos del modelo Sala.
        horarios_data = validated_data.pop("horarios", [])

        # Crear la sala primero
        sala = Sala.objects.create(**validated_data)

        # Crear después los horarios asociados a esa sala
        for horario_data in horarios_data:
            HorarioSala.objects.create(
                sala=sala,
                dia_semana=horario_data["dia_semana"],
                hora_inicio=horario_data["hora_inicio"],
                hora_fin=horario_data["hora_fin"],
            )

        return sala

    def update(self, instance, validated_data):
        # Si vienen horarios en el PATCH/PUT de sala,
        # sustituimos todos los anteriores por los nuevos.
        horarios_data = validated_data.pop("horarios", None)

        # Actualizar los campos simples de la sala
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # Si el cliente ha mandado "horarios", los pisamos completos.
        # Es decir, borramos los antiguos y creamos los nuevos.
        if horarios_data is not None:
            instance.horarios.all().delete()

            for horario_data in horarios_data:
                HorarioSala.objects.create(
                    sala=instance,
                    dia_semana=horario_data["dia_semana"],
                    hora_inicio=horario_data["hora_inicio"],
                    hora_fin=horario_data["hora_fin"],
                )

        return instance

    def to_representation(self, instance):
        # Para la salida queremos devolver los horarios reales asociados
        # a la sala, no el JSON bruto de entrada.
        representation = super().to_representation(instance)
        representation["horarios"] = HorarioSalaSerializer(
            instance.horarios.all(),
            many=True,
            context=self.context,
        ).data
        return representation


class HorarioSalaDetalleSerializer(serializers.ModelSerializer):
    # En el detalle de un horario, devolvemos la sala completa
    # en vez de solo su id.
    sala = SalaSerializer()

    class Meta:
        model = HorarioSala
        fields = ["id", "sala", "dia_semana", "hora_inicio", "hora_fin"]


class SalaDetalleSerializer(serializers.ModelSerializer):
    # En el detalle de una sala, devolvemos todos sus horarios.
    horarios = HorarioSalaSerializer(many=True, read_only=True)

    class Meta:
        model = Sala
        fields = [
            "id",
            "nombre",
            "capacidad",
            "descripcion",
            "image",
            "precio_hora",
            "estado",
            "horarios",
        ]