import csv
from django.core.management.base import BaseCommand
from buses.models import Bus, BusOperator


class Command(BaseCommand):
    help = "Import buses from CSV file"

    def handle(self, *args, **kwargs):

        with open("buses.csv", "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:

                operator = BusOperator.objects.get(
                    name=row["operator"]
                )

                Bus.objects.create(
                    operator=operator,
                    bus_number=row["bus_number"],
                    bus_name=row["bus_name"],
                    bus_type=row["bus_type"],
                    total_seats=row["total_seats"]
                )

        self.stdout.write(
            self.style.SUCCESS("Buses imported successfully!")
        )