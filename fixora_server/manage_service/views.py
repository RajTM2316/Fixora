from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Category

@login_required
def customer_home(request):
    return render(request, "manage_service/customer_home.html")

@login_required
def provider_dashboard(request):
    return render(request, "manage_service/provider_dashboard.html")
def customer_home(request):
    categories = Category.objects.all()
    return render(request, "manage_service/customer_home.html", {
        "categories": categories
    })