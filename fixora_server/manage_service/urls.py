from django.urls import path
from . import views

urlpatterns = [
    path("customer/home/", views.customer_home, name="customer_home"),
    path("provider/dashboard/", views.provider_dashboard, name="provider_dashboard"),
    path("add_category/", views.add_category, name="add_category"),
]
