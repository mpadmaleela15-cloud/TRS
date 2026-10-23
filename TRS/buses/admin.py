from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import BusOperator, Bus, Route, BusSchedule,Seat,Passenger,Booking,BookingSeat,Payment,Cancellation,LiveTracking,Review
admin.site.register(Route)
admin.site.register(BusSchedule)
admin.site.register(BusOperator)
admin.site.register(Bus)
admin.site.register(Seat)
admin.site.register(Passenger)
admin.site.register(Booking)
admin.site.register(BookingSeat)
admin.site.register(Payment)
admin.site.register(Cancellation)
admin.site.register(LiveTracking)
admin.site.register(Review)