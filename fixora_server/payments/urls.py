from django.urls import path
from .views import create_payment, payment_success

urlpatterns = [
    path("pay/<int:request_id>/", create_payment, name="create_payment"),
    path("success/", payment_success, name="payment_success"),
]