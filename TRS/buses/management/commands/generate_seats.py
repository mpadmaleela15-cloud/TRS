from django.core.management.base import BaseCommand
from buses.models import Bus, Seat


class Command(BaseCommand):
    help = "Generate 40 seats for each bus"

    def handle(self, *args, **kwargs):

        seat_layout = [
            ("A1", "Window"),
            ("A2", "Aisle"),
            ("A3", "Aisle"),
            ("A4", "Window"),

            ("B1", "Window"),
            ("B2", "Aisle"),
            ("B3", "Aisle"),
            ("B4", "Window"),

            ("C1", "Window"),
            ("C2", "Aisle"),
            ("C3", "Aisle"),
            ("C4", "Window"),

            ("D1", "Window"),
            ("D2", "Aisle"),
            ("D3", "Aisle"),
            ("D4", "Window"),

            ("E1", "Window"),
            ("E2", "Aisle"),
            ("E3", "Aisle"),
            ("E4", "Window"),

            ("F1", "Window"),
            ("F2", "Aisle"),
            ("F3", "Aisle"),
            ("F4", "Window"),

            ("G1", "Window"),
            ("G2", "Aisle"),
            ("G3", "Aisle"),
            ("G4", "Window"),

            ("H1", "Window"),
            ("H2", "Aisle"),
            ("H3", "Aisle"),
            ("H4", "Window"),

            ("I1", "Window"),
            ("I2", "Aisle"),
            ("I3", "Aisle"),
            ("I4", "Window"),

            ("J1", "Window"),
            ("J2", "Aisle"),
            ("J3", "Aisle"),
            ("J4", "Window"),
        ]

        buses = Bus.objects.all()

        seat_count = 0

        for bus in buses:

            for seat_number, seat_type in seat_layout:

                Seat.objects.get_or_create(
                    bus=bus,
                    seat_number=seat_number,
                    defaults={
                        "seat_type": seat_type
                    }
                )

                seat_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seats generated successfully! "
                f"Processed {seat_count} seats."
            )
        )