from django.db import models
from django.contrib.auth.models import User
# Create your models here
class BusOperator(models.Model):
    name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField()

    def __str__(self):
        return self.name
class Bus(models.Model):
    operator = models.ForeignKey(
        BusOperator,
        on_delete=models.CASCADE
    )
    bus_number = models.CharField(max_length=20)
    bus_name = models.CharField(max_length=100)
    bus_type = models.CharField(max_length=50)
    total_seats = models.IntegerField()

    def __str__(self):
        return self.bus_number    
class Route(models.Model):
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    distance = models.IntegerField()

    def __str__(self):
        return f"{self.source} - {self.destination}"   
class BusSchedule(models.Model):
    bus = models.ForeignKey(
        Bus,
        on_delete=models.CASCADE
    )

    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE
    )

    travel_date = models.DateField()
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    fare = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.bus.bus_number} - {self.route}"    
class Seat(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=10)
    seat_type = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.bus.bus_number} - {self.seat_number}"   
class Passenger(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    phone_number = models.CharField(max_length=15)
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.username  
class Booking(models.Model):
    passenger = models.ForeignKey(
        Passenger,
        on_delete=models.CASCADE
    )

    schedule = models.ForeignKey(
        BusSchedule,
        on_delete=models.CASCADE
    )

    booking_date = models.DateTimeField(auto_now_add=True)

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        default="CONFIRMED"
    )

    def __str__(self):
        return f"Booking {self.id}"       
class BookingSeat(models.Model):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE
    )

    seat = models.ForeignKey(
        Seat,
        on_delete=models.CASCADE
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.booking.id} - {self.seat.seat_number}"    
class Payment(models.Model):
    PAYMENT_METHODS = [
        ("UPI", "UPI"),
        ("CARD", "Card"),
        ("NETBANKING", "Net Banking"),
        ("WALLET", "Wallet"),
    ]

    PAYMENT_STATUS = [
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
        ("REFUNDED", "Refunded"),
    ]

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE
    )

    transaction_id = models.CharField(
        max_length=100,
        unique=True
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS
    )

    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default="PENDING"
    )

    payment_date = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.transaction_id} - {self.status}"    
class Cancellation(models.Model):
    cancellation_status = [
        ("REQUESTED", "Requested"),
        ("APPROVED", "Approved"),
        ("REFUNDED", "Refunded"),
    ]

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE
    )

    reason = models.TextField()

    cancelled_at = models.DateTimeField(
        auto_now_add=True
    )

    refund_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=cancellation_status,
        default="REQUESTED"
    )

    def __str__(self):
        return f"Cancellation - Booking {self.booking.id}"    
class LiveTracking(models.Model):
    bus = models.ForeignKey(
        Bus,
        on_delete=models.CASCADE
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6
    )

    speed = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0
    )

    recorded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.bus.bus_number} - {self.recorded_at}"
class Review(models.Model):
    passenger = models.ForeignKey(
        Passenger,
        on_delete=models.CASCADE
    )

    bus = models.ForeignKey(
        Bus,
        on_delete=models.CASCADE
    )

    rating = models.IntegerField()

    comment = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.bus.bus_number} - {self.rating}/5"        
    