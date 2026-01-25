from django.urls import path
from .views import payment_placeholder

urlpatterns = [
    path('', payment_placeholder, name='payment_placeholder'),
]
