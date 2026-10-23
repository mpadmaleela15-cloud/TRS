import csv
from django.core.management.base import BaseCommand
from buses.models import BusSchedule, Bus, Route
from datetime import datetime


class Command(BaseCommand):
    help = "Import bus schedules from CSV file"

    def handle(self, *args, **kwargs):

        with open("schedules.csv", "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:

                bus = Bus.objects.get(
                    bus_number=row["bus_number"]
                )

                route = Route.objects.get(
                    source=row["source"],
                    destination=row["destination"]
                )

                BusSchedule.objects.create(
                    bus=bus,
                    route=route,
                    travel_date=datetime.strptime(
                        row["travel_date"], "%Y-%m-%d"
                    ).date(),
                    departure_time=datetime.strptime(
                        row["departure_time"], "%H:%M"
                    ).time(),
                    arrival_time=datetime.strptime(
                        row["arrival_time"], "%H:%M"
                    ).time(),
                    fare=row["fare"]
                )

        self.stdout.write(
            self.style.SUCCESS(
                "Bus schedules imported successfully!"
            )
        )