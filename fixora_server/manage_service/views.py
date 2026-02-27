from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.views.decorators.cache import never_cache
from .models import Category, ServiceRequest , ServiceRequestImage
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

    if profile.role != "provider":
        return HttpResponseForbidden("Access denied.")

    provider_services = ProviderService.objects.filter(provider=profile)

    # Incoming PENDING requests
    incoming_requests = ServiceRequest.objects.filter(
        provider_service__provider=profile,
        status="PENDING"
    ).select_related(
        "customer__user",
        "provider_service__service"
    ).order_by("-request_date")

    # Active job
    active_job = ServiceRequest.objects.filter(
        provider_service__provider=profile,
        status="ACCEPTED"
    ).first()

    # Completed jobs
    job_history = ServiceRequest.objects.filter(
        provider_service__provider=profile,
        status="COMPLETED"
    ).order_by("-request_date")

    return render(request, "manage_service/provider_dashboard.html", {
        "profile": profile,
        "provider_services": provider_services,
        "incoming_requests": incoming_requests,
        "active_job": active_job,
        "job_history": job_history,
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

def service_view(request):
    category_id = request.GET.get("category")
    provider_services = ProviderService.objects.filter(
        is_available=True
    ).select_related("service", "provider__user")
    selected_category = None
    categories= Category.objects.filter(is_active=True)
    if category_id:
        provider_services = provider_services.filter(service__category_id=category_id)
        selected_category = Category.objects.filter(id=category_id).first()

    return render(request, "manage_service/service.html", {
        "provider_services": provider_services,
        "selected_category": selected_category,
        "categories": categories
    })

@login_required
def create_request(request):
    profile = get_object_or_404(Profile, user=request.user)

    # Only customers allowed
    if profile.role != "customer":
        return redirect("customer_home")

    # Prevent multiple active bookings
    active_request = ServiceRequest.objects.filter(
        customer=profile,
        status__in=["PENDING", "ACCEPTED"]
    ).exists()

    if active_request:
        messages.error(request, "You already have an active booking.")
        return redirect("my_bookings")

    categories = Category.objects.filter(is_active=True)

    if request.method == "POST":
        category_id = request.POST.get("category")
        description = request.POST.get("description")
        address = request.POST.get("address")

        if not category_id or not address:
            messages.error(request, "Please fill all required fields.")
            return redirect("create_request")

        # Find available provider for selected category
        provider_service = ProviderService.objects.filter(
            service__category_id=category_id,
            is_available=True
        ).select_related("provider", "service").first()

        if not provider_service:
            messages.error(request, "No providers available for this category right now.")
            return redirect("create_request")

        # Create Service Request
        service_request = ServiceRequest.objects.create(
            customer=profile,
            provider_service=provider_service,
            address_text=address,
            problem_description=description,
            status="PENDING"
        )

        # Save uploaded images (multiple)
        images = request.FILES.getlist("images")
        for img in images:
            ServiceRequestImage.objects.create(
                request=service_request,
                image=img
            )

        messages.success(request, "Service request created successfully.")
        return redirect("my_bookings")

    return render(request, "manage_service/create_service_request.html", {
        "categories": categories
    })

@login_required
def accept_request(request, request_id):
    service_request = get_object_or_404(ServiceRequest, id=request_id)
    service_request.status = "Accepted"
    service_request.save()
    return redirect("provider_dashboard")
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

    return redirect("provider_dashboard")
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

    return redirect("provider_dashboard")

# =========================
#Add Service View
# =========================
from .forms import ServiceForm
from .models import ProviderService


def add_service(request):
    # Make sure user is logged in
    if not request.user.is_authenticated:
        return redirect("login")

    profile = request.user.profile

    # Allow only providers
    if profile.role != "provider":
        return HttpResponseForbidden("Access denied.")

    if request.method == "POST":
        form = ServiceForm(request.POST, request.FILES)  
        if form.is_valid():
            service = form.save(commit=False)

            # Automatically set category from provider profile
            service.category = profile.category
            service.save()

            # Create ProviderService entry
            ProviderService.objects.create(
                provider=profile,
                service=service,
                is_available=True
            )

            messages.success(request, "Service created successfully.")
            return redirect("provider_dashboard")

    else:
        form = ServiceForm()

    return render(request, "manage_service/add_service.html", {
        "form": form
    })