from django.db import models

class Room(models.Model):

    number = models.CharField(
        max_length=10,
        unique=True,
        help_text="Room number or code"
    )

    description = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional room description"
    )

    type = models.ForeignKey(
        "RoomType",
        on_delete=models.CASCADE
    )

    image = models.ImageField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Room {self.number} ({self.get_status_display()}) - {self.type.type}"


class RoomType(models.Model):

    name = models.CharField(
        max_length=50,
        help_text="Example: Single Room, Double Room, Suite",
        blank=True
    )

    capacity = models.PositiveSmallIntegerField(
        help_text="Maximum number of people"
    )

    price_per_night = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    amenities = models.ManyToManyField(
        "Amenity",
        blank=True
    )

    def __str__(self):
        return f"{self.name} (capacity {self.capacity}) - ${self.price_per_night}/night"

class Amenity(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
