import csv
from django.core.management.base import BaseCommand
from buses.models import BusOperator
class Command(BaseCommand):
    help = "Import bus operators from CSV file"

    def handle(self, *args, **kwargs):
        with open("operators.csv", "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                BusOperator.objects.create(
                    name=row["name"],
                    contact_number=row["contact_number"],
                    email=row["email"]
                )

        self.stdout.write(
            self.style.SUCCESS("Operators imported successfully!")
        )