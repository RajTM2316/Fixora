from django.urls import path
from . import views
from manage_user.views import save_location
from manage_user.models import Profile

urlpatterns = [
    path("customer/home/", views.customer_home, name="customer_home"),
    path("provider/dashboard/", views.provider_dashboard, name="provider_dashboard"),
    path("add_category/", views.add_category, name="add_category"),
    path('api/save-location/', save_location, name='save_location'),
    path('location-map/', views.location_map, name='location_map'),
    path("provider/toggle-service/<int:service_id>/",views.toggle_service_availability,name="toggle_service_availability"),
    path("my-bookings/", views.my_bookings, name="my_bookings"),
    path("service/", views.service_view, name="service_view"),
    path("create-request/", views.create_request, name="create_request"),
    path("accept-request/<int:request_id>/", views.accept_request, name="accept_request"),
    path("reject-request/<int:request_id>/", views.reject_request, name="reject_request"),
    path("complete-request/<int:request_id>/", views.complete_request, name="complete_request"),
    ]
