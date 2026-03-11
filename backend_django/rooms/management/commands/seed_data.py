from django.core.management.base import BaseCommand
from django.conf import settings
from rooms.models import Room, RoomType, Amenity
from django.core.files import File
from pathlib import Path


class Command(BaseCommand):
    help = "Seed database with initial rooms, room types and amenities"

    def handle(self, *args, **kwargs):

        self.stdout.write("Seeding database...")

        # ---------
        # Amenities
        # ---------

        amenities_list = [
            "Free WiFi",
            "Air conditioning",
            "Private bathroom",
            "Flat screen TV",
            "Ocean view",
            "Balcony",
            "Parking",
            "Spa access"
        ]

        amenities = {}

        for name in amenities_list:
            amenity, _ = Amenity.objects.get_or_create(name=name)
            amenities[name] = amenity

        self.stdout.write("Amenities created")

        # ---------
        # Room Types
        # ---------

        double_room, _ = RoomType.objects.get_or_create(
            name="Classic Double Room",
            capacity=2,
            price_per_night=120
        )

        double_room.amenities.set([
            amenities["Free WiFi"],
            amenities["Air conditioning"],
            amenities["Private bathroom"],
            amenities["Flat screen TV"]
        ])

        superior_room, _ = RoomType.objects.get_or_create(
            name="Superior Double Room",
            capacity=2,
            price_per_night=160
        )

        superior_room.amenities.set([
            amenities["Free WiFi"],
            amenities["Air conditioning"],
            amenities["Private bathroom"],
            amenities["Flat screen TV"],
            amenities["Balcony"]
        ])

        suite_room, _ = RoomType.objects.get_or_create(
            name="Junior Suite",
            capacity=3,
            price_per_night=220
        )

        suite_room.amenities.set([
            amenities["Free WiFi"],
            amenities["Air conditioning"],
            amenities["Private bathroom"],
            amenities["Flat screen TV"],
            amenities["Ocean view"],
            amenities["Spa access"]
        ])

        self.stdout.write("Room types created")

        # ---------
        # Rooms
        # ---------

        seed_images = Path(settings.MEDIA_ROOT) / "seed_rooms"

        rooms_data = [
            ("101", "Classic double room", double_room, "room1.jpeg"),
            ("102", "Classic double room", double_room, "room2.jpeg"),
            ("201", "Superior room with balcony", superior_room, "room3.jpeg"),
            ("301", "Junior suite with ocean view", suite_room, "room4.jpeg"),
        ]

        for number, desc, room_type, img in rooms_data:

            room, created = Room.objects.get_or_create(
                number=number,
                defaults={
                    "description": desc,
                    "type": room_type
                }
            )

            if created:
                image_path = seed_images / img

                if image_path.exists():
                    with open(image_path, "rb") as f:
                        room.image.save(img, File(f), save=True)

        self.stdout.write(self.style.SUCCESS("Seed completed!"))
