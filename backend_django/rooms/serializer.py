from rest_framework import serializers
from .models import Room, RoomType, Amenity


class RoomTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = RoomType
        fields = ['id', 'name', 'capacity', 'price_per_night']


class RoomSerializer(serializers.ModelSerializer):

    type = serializers.PrimaryKeyRelatedField(
        queryset=RoomType.objects.all()
    )

    class Meta:
        model = Room
        fields = [
            'id',
            'number',
            'description',
            'type',
            'created_at',
            'updated_at'
        ]

        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['type'] = RoomTypeSerializer(instance.type).data
        return ret

class AmenitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Amenity
        fields = ['id', 'name']
        read_only_fields = ['id']
