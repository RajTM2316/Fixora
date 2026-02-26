from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.views.decorators.cache import never_cache
from .models import Category, ServiceRequest
from manage_user.models import Profile
from manage_service.models import ProviderService
from django.contrib.admin.views.decorators import staff_member_required
from .models import Category
# =========================
# PROVIDER DASHBOARD
# =========================
@login_required
@never_cache
def provider_dashboard(request):
    profile = get_object_or_404(Profile, user=request.user)

    # Optional role protection
    if profile.role != "provider":
        return HttpResponseForbidden("Access denied.")

    provider_services = ProviderService.objects.filter(provider=profile)

    return render(request, "manage_service/provider_dashboard.html", {
        "profile": profile,
        "provider_services": provider_services,
        "incoming_requests": [],
        "active_job": None,
        "job_history": [],
    })


# =========================
# TOGGLE SERVICE AVAILABILITY
# =========================
@login_required
def toggle_service_availability(request, service_id):
    profile = get_object_or_404(Profile, user=request.user)

    if profile.role != "provider":
        return HttpResponseForbidden("Access denied.")

    if request.method == "POST":
        provider_service = get_object_or_404(
            ProviderService,
            id=service_id,
            provider=profile
        )

        provider_service.is_available = bool(request.POST.get("is_available"))
        provider_service.save()

    return redirect("provider_dashboard")


# =========================
# CUSTOMER HOME
# =========================
@login_required
@never_cache
def customer_home(request):
    profile = get_object_or_404(Profile, user=request.user)

    if profile.role != "customer":
        return HttpResponseForbidden("Access denied.")

    categories = Category.objects.filter(is_active=True)

    return render(request, "manage_service/customer_home.html", {
        "categories": categories
    })


# =========================
# ADD CATEGORY (ADMIN ONLY)
# =========================
@staff_member_required
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

        Category.objects.create(
            name=name,
            description=description,
            image=image,
            is_active=is_active,
            estimated_time=estimated_time,
            estimated_price=estimated_price
        )

        messages.success(request, "Category added successfully.")
        return redirect("add_category")

    return render(request, "manage_service/add_category.html")


# =========================
# LOCATION MAP
# =========================
@login_required
def location_map(request):
    profile = get_object_or_404(Profile, user=request.user)

    return render(request, "manage_service/location_map.html", {
        "latitude": profile.latitude,
        "longitude": profile.longitude
    })


# =========================
# MY BOOKINGS
# =========================
@login_required
def my_bookings(request):
    profile = get_object_or_404(Profile, user=request.user)

    if profile.role != "customer":
        return HttpResponseForbidden("Access denied.")

    bookings = ServiceRequest.objects.filter(
        customer=profile
    ).select_related(
        "provider_service__service__category",
        "provider_service__provider"
    ).order_by("-request_date")

    return render(request, "manage_service/my_bookings.html", {
        "bookings": bookings
    })

# =========================
# SERVICE VIEW 
# ========================= 

from django.shortcuts import render

def service_view(request):
    category_id = request.GET.get("category")
    provider_services = ProviderService.objects.filter(is_available=True)
    selected_category = None

    if category_id:
        provider_services = provider_services.filter(service__category_id=category_id)
        selected_category = Category.objects.filter(id=category_id).first()

    return render(request, "manage_service/service.html", {
        "provider_services": provider_services,
        "selected_category": selected_category
    })