from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("search/", views.search_buses, name="search_buses"),
    path("select-seat/<int:schedule_id>/", views.select_seat, name="select_seat"),
    path("passenger-details/<int:schedule_id>/<str:seat_number>/",views.passenger_details,name="passenger_details"),
    path("payment/<int:booking_id>/", views.payment, name="payment"),
    path( "confirmation/<int:booking_id>/",views.confirmation,name="confirmation"),
    path( "my-bookings/",views.my_bookings,name="my_bookings"),
    path("cancel-booking/<int:booking_id>/",views.cancel_booking, name="cancel_booking"),
    path("live-tracking/<int:bus_id>/", views.live_tracking, name="live_tracking"),
    path("review/<int:bus_id>/",views.review_bus, name="review_bus"),
    path("admin-dashboard/",views.admin_dashboard,name="admin_dashboard"),
    path("register/", views.register_user, name="register"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
]