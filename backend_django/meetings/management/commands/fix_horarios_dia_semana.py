from django.core.management.base import BaseCommand

from meetings.models import HorarioSala


class Command(BaseCommand):
    help = "Asigna un dia_semana por defecto a horarios con valor nulo."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dia",
            type=int,
            default=0,
            help="Dia de la semana a asignar (0=Lunes ... 6=Domingo).",
        )

    def handle(self, *args, **options):
        dia = options["dia"]
        if dia < 0 or dia > 6:
            self.stderr.write("El parametro --dia debe estar entre 0 y 6.")
            return

        qs = HorarioSala.objects.filter(dia_semana__isnull=True)
        total = qs.count()
        if total == 0:
            self.stdout.write("No hay horarios con dia_semana nulo.")
            return

        qs.update(dia_semana=dia)
        self.stdout.write(f"Horarios actualizados: {total} (dia_semana={dia})")
