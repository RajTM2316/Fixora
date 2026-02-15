from django.urls import path
from . import views
from manage_user.views import save_location
urlpatterns = [
    path("customer/home/", views.customer_home, name="customer_home"),
    path("provider/dashboard/", views.provider_dashboard, name="provider_dashboard"),
    path("add_category/", views.add_category, name="add_category"),
    path('api/save-location/', save_location, name='save_location')
]
