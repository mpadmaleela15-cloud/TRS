import csv
from django.core.management.base import BaseCommand
from buses.models import Route


class Command(BaseCommand):
    help = "Import routes from CSV file"

    def handle(self, *args, **kwargs):

        with open("routes.csv", "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                Route.objects.create(
                    source=row["source"],
                    destination=row["destination"],
                    distance=row["distance"]
                )

        self.stdout.write(
            self.style.SUCCESS("Routes imported successfully!")
        )