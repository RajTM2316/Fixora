# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Category
from django.contrib import messages
from manage_user.views import save_location
from manage_user.models import Profile
from manage_service.models import ProviderService
from .models import ServiceRequest

@login_required
def provider_dashboard(request):
    profile = Profile.objects.get(user=request.user)

    provider_services = ProviderService.objects.filter(provider=profile)

    # keep your existing logic for these if already defined
    incoming_requests = []
    active_job = None
    job_history = []
    # Hard coded values for now
    return render(request, "manage_service/provider_dashboard.html", {
        "profile": profile,
        "provider_services": provider_services,
        "incoming_requests": incoming_requests,
        "active_job": active_job,
        "job_history": job_history,
    })

@login_required
def toggle_service_availability(request, service_id):
    if request.method == "POST":
        profile = Profile.objects.get(user=request.user)

        try:
            provider_service = ProviderService.objects.get(
                id=service_id,
                provider=profile
            )
        except ProviderService.DoesNotExist:
            return redirect("provider_dashboard")

        provider_service.is_available = bool(request.POST.get("is_available"))
        provider_service.save()

    return redirect("provider_dashboard")

@login_required
def customer_home(request):
    categories = Category.objects.filter(is_active=True)
    return render(request, "manage_service/customer_home.html", {
        "categories": categories
    })

@login_required
def add_category(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        image = request.FILES.get("image")
        is_active = bool(request.POST.get("is_active"))
        estimated_time = request.POST.get("estimated_time")
        estimated_price = request.POST.get("estimated_price")
        if Category.objects.filter(name=name).exists():
            messages.error(request, "Category with this name already exists.")
            return redirect("add_category")
        else:
            Category.objects.create(name=name, description=description, image=image, is_active=is_active, estimated_time=estimated_time, estimated_price=estimated_price)
            messages.success(request, "Category added successfully.")
            return redirect("add_category")
    return render(request, "manage_service/add_category.html")

@login_required
def location_map(request):
    profile = Profile.objects.get(user=request.user)

    return render(request, "manage_service/location_map.html", {
        "latitude": profile.latitude,
        "longitude": profile.longitude
    })

@login_required
def my_bookings(request):
    profile = Profile.objects.get(user=request.user)

    bookings = ServiceRequest.objects.filter(
        customer=profile
    ).select_related(
        "provider_service__service__category",
        "provider_service__provider"
    ).order_by("-request_date")

    return render(request, "manage_service/my_bookings.html", {
        "bookings": bookings
    })