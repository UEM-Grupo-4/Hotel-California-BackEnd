from django.core.management.base import BaseCommand

from meetings.models import HorarioSala


class Command(BaseCommand):
    help = "Revisa horarios con dia_semana nulo y muestra conteo total."

    def handle(self, *args, **options):
        total = HorarioSala.objects.count()
        nulos = HorarioSala.objects.filter(dia_semana__isnull=True).count()

        self.stdout.write(f"Total horarios: {total}")
        self.stdout.write(f"Horarios con dia_semana nulo: {nulos}")

        if nulos:
            self.stdout.write("Detalles (id, sala_id, hora_inicio, hora_fin):")
            for h in HorarioSala.objects.filter(dia_semana__isnull=True).only(
                "id", "sala_id", "hora_inicio", "hora_fin"
            ):
                self.stdout.write(
                    f"- id={h.id} sala_id={h.sala_id} {h.hora_inicio}-{h.hora_fin}"
                )
