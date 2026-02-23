# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Category
from django.contrib import messages
from manage_user.views import save_location
from manage_user.models import Profile
@login_required
def provider_dashboard(request):
    return render(request, "manage_service/provider_dashboard.html")
def customer_home(request):
    categories = Category.objects.filter(is_active=True)
    return render(request, "manage_service/customer_home.html", {
        "categories": categories
    })

def add_category(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        image = request.FILES.get("image")
        is_active = bool(request.POST.get("is_active"))
        if Category.objects.filter(name=name).exists():
            messages.error(request, "Category with this name already exists.")
            return redirect("add_category")
        else:
            Category.objects.create(name=name, description=description, image=image, is_active=is_active)
            messages.success(request, "Category added successfully.")
            return redirect("add_category")
    return render(request, "manage_service/add_category.html")

def location_map(request):
    profile = Profile.objects.get(user=request.user)

    return render(request, "manage_service/location_map.html", {
        "latitude": profile.latitude,
        "longitude": profile.longitude
    })