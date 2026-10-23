from django.contrib.auth.models import User
from django.shortcuts import render,redirect
from .models import (BusSchedule, Bus,Seat, Passenger,Booking,BookingSeat,Payment,Cancellation,LiveTracking,Review)
import uuid
from django.db.models import Prefetch, Avg
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
def home(request):
    return render(request, "home.html")
def search_buses(request):
    source = request.GET.get("from")
    destination = request.GET.get("to")
    travel_date = request.GET.get("date")

    print("SOURCE:", source)
    print("DESTINATION:", destination)
    print("DATE:", travel_date)

    schedules = BusSchedule.objects.filter(
        route__source__iexact=source,
        route__destination__iexact=destination,
        travel_date=travel_date
    ).select_related("bus", "route")

    print("RESULTS:", schedules)

    now = timezone.now()
    one_hour_ago = now - timedelta(hours=1)

    for schedule in schedules:

        recent_bookings = Booking.objects.filter(
            schedule=schedule,
            booking_date__gte=one_hour_ago,
            status__in=["PENDING", "CONFIRMED"]
        ).count()

        if recent_bookings >= 5:
            probability = 90
            activity = "🔥 High booking activity"

        elif recent_bookings >= 3:
            probability = 72
            activity = "🔥 High booking activity"

        elif recent_bookings == 2:
            probability = 55
            activity = "🟡 Moderate booking activity"

        elif recent_bookings == 1:
            probability = 35
            activity = "🟡 Moderate booking activity"

        else:
            probability = 15
            activity = "🟢 Low booking activity"

        schedule.booking_probability = probability
        schedule.booking_activity = activity

    return render(request, "bus_results.html", {
        "schedules": schedules,
        "source": source,
        "destination": destination,
        "travel_date": travel_date,
    })
def select_seat(request, schedule_id):
    schedule = BusSchedule.objects.select_related(
        "bus",
        "route"
    ).get(id=schedule_id)

    seats = Seat.objects.filter(
        bus=schedule.bus
    ).order_by("seat_number")

    return render(request, "seat_selection.html", {
        "schedule": schedule,
        "seats": seats,
    })
def passenger_details(request, schedule_id, seat_number):

    schedule = BusSchedule.objects.select_related(
        "bus",
        "route"
    ).get(id=schedule_id)

    if request.method == "POST":

        name = request.POST.get("name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")

        # Find or create User
        user = User.objects.filter(email=email).first()

        if user is None:

            username = email.split("@")[0]

            original_username = username
            counter = 1

            while User.objects.filter(username=username).exists():
                username = f"{original_username}{counter}"
                counter += 1

            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=name
            )

        # Find or create Passenger
        passenger = Passenger.objects.filter(user=user).first()

        if passenger is None:

            passenger = Passenger.objects.create(
                user=user,
                phone_number=phone
            )

        else:

            request.session["passenger_id"]=passenger.id

        # Find selected seat
        seat = Seat.objects.filter(
            bus=schedule.bus,
            seat_number=seat_number
        ).first()

        if seat is None:
            return render(request, "passenger_details.html", {
                "schedule": schedule,
                "seat_number": seat_number,
                "message": "Selected seat does not exist."
            })

        # Check whether this seat is already booked
        already_booked = BookingSeat.objects.filter(
            seat=seat,
            booking__schedule=schedule,
            booking__status__in=["PENDING", "CONFIRMED"]
        ).exists()

        if already_booked:
            return render(request, "passenger_details.html", {
                "schedule": schedule,
                "seat_number": seat_number,
                "message": "Sorry, this seat is already booked."
            })

        # Create Booking
        booking = Booking.objects.create(
            passenger=passenger,
            schedule=schedule,
            total_amount=schedule.fare,
            status="PENDING"
        )

        # Create BookingSeat
        BookingSeat.objects.create(
            booking=booking,
            seat=seat,
            price=schedule.fare
        )

        return redirect("payment", booking_id=booking.id)
        

    return render(request, "passenger_details.html", {
        "schedule": schedule,
        "seat_number": seat_number,
    })
def payment(request, booking_id):

    booking = Booking.objects.select_related(
        "passenger",
        "schedule",
        "schedule__bus",
        "schedule__route"
    ).get(id=booking_id)

    booking_seat = BookingSeat.objects.filter(
        booking=booking
    ).first()

    if request.method == "POST":

        payment_method = request.POST.get("payment_method")

        # Check whether payment already exists
        existing_payment = Payment.objects.filter(
            booking=booking
        ).first()

        if existing_payment:

            return render(request, "payment.html", {
                "booking": booking,
                "seat_number": booking_seat.seat.seat_number,
                "message": "Payment has already been completed."
            })

        # Generate a unique transaction ID
        transaction_id = "TRS-" + uuid.uuid4().hex[:12].upper()

        # Create payment
        payment = Payment.objects.create(
            booking=booking,
            transaction_id=transaction_id,
            amount=booking.total_amount,
            payment_method=payment_method,
            status="SUCCESS"
        )

        # Confirm booking
        booking.status = "CONFIRMED"
        booking.save()

        return redirect("confirmation",booking_id=booking.id)

    return render(request, "payment.html", {
        "booking": booking,
        "seat_number": booking_seat.seat.seat_number,
    })
def confirmation(request, booking_id):

    booking = Booking.objects.select_related(
        "passenger",
        "passenger__user",
        "schedule",
        "schedule__bus",
        "schedule__route"
    ).get(id=booking_id)
    request.session["passenger_id"] = booking.passenger.id

    booking_seat = BookingSeat.objects.filter(
        booking=booking
    ).first()

    payment = Payment.objects.get(
        booking=booking
    )

    return render(request, "confirmation.html", {
        "booking": booking,
        "seat_number": booking_seat.seat.seat_number,
        "payment": payment,
    })
@login_required(login_url="login")
def my_bookings(request):

    passenger_id = request.session.get("passenger_id")

    if not passenger_id:
        return render(request, "my_bookings.html", {
            "bookings": [],
            "message": "You don't have any bookings yet."
        })

    passenger = Passenger.objects.filter(
        id=passenger_id,
        user=request.user
    ).first()

    if not passenger:
        return render(request, "my_bookings.html", {
            "bookings": [],
            "message": "You don't have any bookings yet."
        })

    bookings = Booking.objects.filter(
        passenger=passenger
    ).select_related(
        "schedule",
        "schedule__bus",
        "schedule__route",
        "payment"
    ).prefetch_related(
        Prefetch(
            "bookingseat_set",
            queryset=BookingSeat.objects.select_related("seat"),
            to_attr="booking_seats"
        )
    ).order_by("-booking_date")

    return render(request, "my_bookings.html", {
        "bookings": bookings
    })
def cancel_booking(request, booking_id):

    booking = Booking.objects.select_related(
        "passenger",
        "schedule",
        "schedule__bus",
        "schedule__route"
    ).get(id=booking_id)

    # Make sure this booking belongs to the current passenger
    passenger_id = request.session.get("passenger_id")

    if passenger_id != booking.passenger.id:
        return render(request, "cancel_booking.html", {
            "message": "You are not authorized to cancel this booking."
        })

    # Check if booking is already cancelled
    if booking.status == "CANCELLED":
        return render(request, "cancel_booking.html", {
            "booking": booking,
            "message": "This booking has already been cancelled."
        })

    if request.method == "POST":

        reason = request.POST.get("reason")

        if not reason:
            return render(request, "cancel_booking.html", {
                "booking": booking,
                "message": "Please enter a cancellation reason."
            })

        # Create cancellation record
        cancellation = Cancellation.objects.create(
            booking=booking,
            reason=reason,
            refund_amount=booking.total_amount,
            status="REFUNDED"
        )

        # Change booking status
        booking.status = "CANCELLED"
        booking.save()

        # Update payment status
        payment = Payment.objects.filter(
            booking=booking
        ).first()

        if payment:
            payment.status = "REFUNDED"
            payment.save()

        return render(request, "cancel_booking.html", {
            "booking": booking,
            "cancellation": cancellation,
            "message": "Booking cancelled successfully. Refund processed."
        })

    return render(request, "cancel_booking.html", {
        "booking": booking
    })
def live_tracking(request, bus_id):

    bus = Bus.objects.get(id=bus_id)

    tracking = LiveTracking.objects.filter(
        bus=bus
    ).order_by("-recorded_at").first()

    return render(request, "live_tracking.html", {
        "bus": bus,
        "tracking": tracking,
    })
def review_bus(request, bus_id):

    bus = Bus.objects.get(id=bus_id)

    passenger_id = request.session.get("passenger_id")

    if not passenger_id:
        return render(request, "review.html", {
            "bus": bus,
            "message": "Please complete a booking before submitting a review."
        })

    passenger = Passenger.objects.get(id=passenger_id)

    if request.method == "POST":

        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        if not rating:
            reviews = Review.objects.filter(bus=bus).select_related(
                "passenger",
                "passenger__user"
            )

            average_rating = reviews.aggregate(
                average=Avg("rating")
            )["average"]

            return render(request, "review.html", {
                "bus": bus,
                "reviews": reviews,
                "average_rating": average_rating,
                "message": "Please select a rating."
            })

        Review.objects.create(
            passenger=passenger,
            bus=bus,
            rating=rating,
            comment=comment
        )

        message = "Thank you! Your review has been submitted successfully."

    else:
        message = None

    reviews = Review.objects.filter(
        bus=bus
    ).select_related(
        "passenger",
        "passenger__user"
    ).order_by("-created_at")

    average_rating = reviews.aggregate(
        average=Avg("rating")
    )["average"]

    return render(request, "review.html", {
        "bus": bus,
        "reviews": reviews,
        "average_rating": average_rating,
        "message": message
    })
@user_passes_test(lambda user: user.is_staff)
def admin_dashboard(request):

    total_buses = Bus.objects.count()
    total_schedules = BusSchedule.objects.count()
    total_bookings = Booking.objects.count()
    total_payments = Payment.objects.count()
    total_cancellations = Cancellation.objects.count()
    total_reviews = Review.objects.count()

    confirmed_bookings = Booking.objects.filter(
        status="CONFIRMED"
    ).count()

    cancelled_bookings = Booking.objects.filter(
        status="CANCELLED"
    ).count()

    successful_payments = Payment.objects.filter(
        status="SUCCESS"
    ).count()

    refunded_payments = Payment.objects.filter(
        status="REFUNDED"
    ).count()

    return render(request, "admin_dashboard.html", {
        "total_buses": total_buses,
        "total_schedules": total_schedules,
        "total_bookings": total_bookings,
        "total_payments": total_payments,
        "total_cancellations": total_cancellations,
        "total_reviews": total_reviews,
        "confirmed_bookings": confirmed_bookings,
        "cancelled_bookings": cancelled_bookings,
        "successful_payments": successful_payments,
        "refunded_payments": refunded_payments,
    })
def register_user(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {
                "message": "Username already exists."
            })

        if User.objects.filter(email=email).exists():
            return render(request, "register.html", {
                "message": "Email already exists."
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)

        return redirect("home")

    return render(request, "register.html")


def login_user(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect("home")

        return render(request, "login.html", {
            "message": "Invalid username or password."
        })

    return render(request, "login.html")


def logout_user(request):

    logout(request)

    return redirect("home")