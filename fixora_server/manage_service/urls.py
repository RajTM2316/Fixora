from django.urls import path
from . import views

app_name = "manage_service"

urlpatterns = [

    # =========================
    # CUSTOMER ROUTES
    # =========================
    path("home/", views.customer_home, name="customer_home"),
    path("my-bookings/", views.my_bookings, name="my_bookings"),
    path("create-request/", views.create_request, name="create_request"),
    path("booking/<int:booking_id>/", views.booking_detail, name="booking_detail"),

    # =========================
    # SERVICES
    # =========================
    path("services/", views.service_view, name="service_view"),
    path("book/<int:ps_id>/", views.book_service, name="book_service"),

    # =========================
    # PROVIDER ROUTES
    # =========================
    path("provider/dashboard/", views.provider_dashboard, name="provider_dashboard"),
    path("provider/accept/<int:request_id>/", views.accept_request, name="accept_request"),
    path("provider/reject/<int:request_id>/", views.reject_request, name="reject_request"),
    path("provider/complete/<int:request_id>/", views.complete_request, name="complete_request"),

    # =========================
    # ADMIN ROUTES
    # =========================
    path("admin/add-category/", views.add_category, name="add_category"),
    path("admin/add-service/", views.add_service, name="add_service"),

    # =========================
    # LOCATION
    # =========================
]