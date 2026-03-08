from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction

from .models import Category, ServiceRequest, ServiceRequestImage, ProviderService
from .forms import ServiceForm
from manage_user.models import Profile


# =========================
# PROVIDER DASHBOARD
# =========================
@login_required
@never_cache
def provider_dashboard(request):
    profile = get_object_or_404(Profile, user=request.user)

    if profile.role != "provider":
        return HttpResponseForbidden("Access denied.")
    
    if request.method == "POST" and "toggle_availability" in request.POST:
        services = ProviderService.objects.filter(provider=profile)
        new_status = not services.first().is_available if services.exists() else True
        services.update(is_available=new_status)
        return redirect("manage_service:provider_dashboard")

    provider_services = ProviderService.objects.filter(provider=profile)

    incoming_requests = ServiceRequest.objects.filter(
        provider_service__provider=profile,
        status="PENDING"
    ).select_related(
        "customer__user",
        "provider_service__service"
    ).order_by("-request_date")

    active_job = ServiceRequest.objects.filter(
        provider_service__provider=profile,
        status="ACCEPTED"
    ).first()

    job_history = ServiceRequest.objects.filter(
        provider_service__provider=profile,
        status="COMPLETED"
    ).order_by("-request_date")

    return render(request, "provider/provider_dashboard.html", {
        "profile": profile,
        "provider_services": provider_services,
        "incoming_requests": incoming_requests,
        "active_job": active_job,
        "job_history": job_history,
    })


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

    active_booking = ServiceRequest.objects.filter(
        customer=profile,
        status__in=["PENDING", "ACCEPTED"]
    ).first()

    available_providers = ProviderService.objects.filter(is_available=True)

    return render(request, "customer/customer_home.html", {
        "categories": categories,
        "active_booking": active_booking,
        "available_providers": available_providers
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
        "provider_service__service",
        "provider_service__provider__user"
    ).order_by("-request_date")

    return render(request, "customer/my_bookings.html", {
        "bookings": bookings
    })


# =========================
# SERVICE LISTING
# =========================
def service_view(request):
    category_id = request.GET.get("category")

    provider_services = ProviderService.objects.filter(
        is_available=True
    ).select_related("service", "provider__user")

    selected_category = None
    categories = Category.objects.filter(is_active=True)

    if category_id:
        provider_services = provider_services.filter(service__category_id=category_id)
        selected_category = Category.objects.filter(id=category_id).first()

    return render(request, "services/service.html", {
        "provider_services": provider_services,
        "selected_category": selected_category,
        "categories": categories
    })


# =========================
# CREATE SERVICE REQUEST
# =========================
@login_required
@transaction.atomic
def create_request(request):
    profile = get_object_or_404(Profile, user=request.user)

    if profile.role != "customer":
        return redirect("manage_service:customer_home")

    if ServiceRequest.objects.filter(
        customer=profile,
        status__in=["PENDING", "ACCEPTED"]
    ).exists():
        messages.error(request, "You already have an active booking.")
        return redirect("manage_service:my_bookings")

    categories = Category.objects.filter(is_active=True)

    if request.method == "POST":
        category_id = request.POST.get("category")
        description = request.POST.get("description")
        address = request.POST.get("address")

        if not category_id or not address:
            messages.error(request, "Please fill all required fields.")
            return redirect("manage_service:create_request")

        provider_service = ProviderService.objects.filter(
            service__category_id=category_id,
            is_available=True
        ).select_related("provider", "service").first()

        if not provider_service:
            messages.error(request, "No providers available right now.")
            return redirect("manage_service:create_request")

        service_request = ServiceRequest.objects.create(
            customer=profile,
            provider_service=provider_service,
            address_text=address,
            problem_description=description,
            status="PENDING"
        )

        for img in request.FILES.getlist("images"):
            ServiceRequestImage.objects.create(
                request=service_request,
                image=img
            )

        messages.success(request, "Service request created successfully.")
        return redirect("manage_service:my_bookings")

    return render(request, "services/create_service_request.html", {
        "categories": categories
    })


# =========================
# BOOK SERVICE
# =========================
@login_required
@transaction.atomic
def book_service(request, ps_id):
    profile = get_object_or_404(Profile, user=request.user)

    if profile.role != "customer":
        return HttpResponseForbidden("Access denied.")

    provider_service = get_object_or_404(
        ProviderService.objects.select_related("provider__user", "service"),
        id=ps_id,
        is_available=True
    )

    if ServiceRequest.objects.filter(
        customer=profile,
        status__in=["PENDING", "ACCEPTED"]
    ).exists():
        messages.error(request, "You already have an active booking.")
        return redirect("manage_service:my_bookings")

    if request.method == "POST":
        address = request.POST.get("address")
        description = request.POST.get("description")

        if not address:
            messages.error(request, "Address is required.")
            return redirect("manage_service:book_service", ps_id=ps_id)

        service_request = ServiceRequest.objects.create(
            customer=profile,
            provider_service=provider_service,
            address_text=address,
            problem_description=description,
            status="PENDING"
        )

        for img in request.FILES.getlist("images"):
            ServiceRequestImage.objects.create(
                request=service_request,
                image=img
            )

        messages.success(request, "Booking placed successfully.")
        return redirect("manage_service:my_bookings")

    return render(request, "services/book_service.html", {
        "provider_service": provider_service
    })


# =========================
# BOOKING DETAIL
# =========================
@login_required
def booking_detail(request, booking_id):
    profile = get_object_or_404(Profile, user=request.user)

    if profile.role != "customer":
        return HttpResponseForbidden("Access denied.")

    booking = get_object_or_404(
        ServiceRequest,
        id=booking_id,
        customer=profile
    )

    return render(request, "services/booking_detail.html", {
        "booking": booking
    })


# =========================
# PROVIDER ACTIONS
# =========================
@login_required
def accept_request(request, request_id):
    profile = get_object_or_404(Profile, user=request.user)

    if profile.role != "provider":
        return HttpResponseForbidden("Access denied.")

    if ServiceRequest.objects.filter(
        provider_service__provider=profile,
        status="ACCEPTED"
    ).exists():
        messages.error(request, "You already have an active job.")
        return redirect("manage_service:provider_dashboard")

    service_request = ServiceRequest.objects.filter(
        id=request_id,
        provider_service__provider=profile,
        status="PENDING"
    ).first()

    if not service_request:
        messages.error(request, "Invalid request.")
        return redirect("manage_service:provider_dashboard")
    
    lat=request.GET.get("latitude")
    lng=request.GET.get("longitude")

    print("Provider Lat:", lat)
    print("Provider Lng:", lng)

    if lat and lng:
        profile.latitude = lat
        profile.longitude = lng
        profile.save()

    service_request.status = "ACCEPTED"
    service_request.save()

    messages.success(request, "Request accepted successfully.")
    return redirect("manage_service:provider_dashboard")


@login_required
def reject_request(request, request_id):
    profile = get_object_or_404(Profile, user=request.user)

    if profile.role != "provider":
        return HttpResponseForbidden("Access denied.")

    service_request = get_object_or_404(
        ServiceRequest,
        id=request_id,
        provider_service__provider=profile
    )

    service_request.status = "REJECTED"
    service_request.save()

    return redirect("manage_service:provider_dashboard")


@login_required
def complete_request(request, request_id):
    profile = get_object_or_404(Profile, user=request.user)

    if profile.role != "provider":
        return HttpResponseForbidden("Access denied.")

    service_request = get_object_or_404(
        ServiceRequest,
        id=request_id,
        provider_service__provider=profile,
        status="ACCEPTED"
    )

    service_request.status = "COMPLETED"
    service_request.save()

    return redirect("manage_service:provider_dashboard")


# =========================
# ADD CATEGORY (ADMIN)
# =========================
@staff_member_required
def add_category(request):
    if request.method == "POST":
        name = request.POST.get("name")

        if Category.objects.filter(name=name).exists():
            messages.error(request, "Category already exists.")
            return redirect("/admin/")

        Category.objects.create(
            name=name,
            description=request.POST.get("description"),
            image=request.FILES.get("image"),
            is_active = bool(request.POST.get("is_active")),
            estimated_time=request.POST.get("estimated_time"),
            estimated_price=request.POST.get("estimated_price"),
        )

        messages.success(request, "Category added successfully.")
        return redirect("/admin/")

    return render(request, "admin/add_category.html")


# =========================
# ADD SERVICE (PROVIDER)
# =========================
@login_required
def add_service(request):
    profile = get_object_or_404(Profile, user=request.user)

    if profile.role != "provider":
        return HttpResponseForbidden("Access denied.")

    if request.method == "POST":
        form = ServiceForm(request.POST, request.FILES)

        if form.is_valid():
            service = form.save(commit=False)
            service.category = profile.category
            service.save()

            ProviderService.objects.create(
                provider=profile,
                service=service,
                is_available=True
            )

            messages.success(request, "Service created successfully.")
            return redirect("manage_service:provider_dashboard")

    else:
        form = ServiceForm()

    return render(request, "admin/add_service.html", {
        "form": form
    })


# =========================
# LOCATION MAP
# =========================
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
@csrf_exempt
def save_location(request):
    if request.method == "POST":
        data = json.loads(request.body)
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        if request.user.is_authenticated:
            profile = Profile.objects.get(user=request.user)
            profile.latitude = latitude
            profile.longitude = longitude
            profile.save()
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse({"status": "error", "message": "User not authenticated"}, status=401)

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

@login_required
def location_map(request):
    profile = Profile.objects.get(user=request.user)

    return render(request, "standalone/location_map.html", {
        "latitude": profile.latitude,
        "longitude": profile.longitude
    })

@login_required
def track_provider(request, request_id):

    service_request = get_object_or_404(ServiceRequest, id=request_id)

    provider_profile = service_request.provider_service.provider

    context = {
        "provider": provider_profile
    }

    return render(request, "standalone/track_provider.html", context)
# =========================
# ACTIVATE/DEACTIVATE CATEGORY (ADMIN)
# =========================
@staff_member_required
def admin_category_list(request):
    categories = Category.objects.all()
    return render(request, "admin/activate_category.html", {
        "categories": categories
    })


@staff_member_required
def toggle_category_status(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.is_active = not category.is_active
    category.save()
    return redirect("manage_service:admin_category_list")