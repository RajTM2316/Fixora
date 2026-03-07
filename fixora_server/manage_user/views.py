from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .models import Profile, Address
from manage_service.models import Category
import json


# =========================
# LOGIN
# =========================
@never_cache
def login_view(request):

    # -------------------------
    # If already logged in
    # -------------------------
    if request.user.is_authenticated:

        # Block superuser from normal dashboard
        if request.user.is_superuser:
            return redirect("admin:index")

        profile, _ = Profile.objects.get_or_create(user=request.user)

        if profile.role == "provider":
            return redirect("manage_service:provider_dashboard")
        else:
            return redirect("manage_service:customer_home")


    # -------------------------
    # Handle POST Login
    # -------------------------
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        selected_role = request.POST.get("role")

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Invalid username or password.")
            return render(request, "manage_user/login.html")

        # Block superuser from normal login
        if user.is_superuser:
            messages.error(request, "Admin users must login from admin panel.")
            return redirect("admin:login")

        profile, _ = Profile.objects.get_or_create(user=user)

        # Role mismatch check
        if profile.role != selected_role:
            messages.error(request, "Incorrect role selected.")
            return render(request, "manage_user/login.html")

        # All checks passed
        login(request, user)

        if profile.role == "provider":
            return redirect("manage_service:provider_dashboard")
        else:
            return redirect("manage_service:customer_home")

    return render(request, "manage_user/login.html")


# =========================
# SIGNUP
# =========================
def signup_view(request):
    categories = Category.objects.filter(is_active=True)
    selected_role = request.POST.get("role", "customer")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role")

        profile_picture = request.FILES.get("profile_picture")
        phone = request.POST.get("phone")

        street = request.POST.get("street")
        city = request.POST.get("city")
        pincode = request.POST.get("pincode")

        category_id = request.POST.get("category")
        category = Category.objects.filter(id=category_id).first() if category_id else None

        # -------------------------
        # Validation
        # -------------------------
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "manage_user/sign_up.html", {
                "categories": categories,
                "selected_role": selected_role
            })

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, "manage_user/sign_up.html", {
                "categories": categories,
                "selected_role": selected_role
            })

        if role == "provider" and not category:
            messages.error(request, "Service providers must select a category.")
            return render(request, "manage_user/sign_up.html", {
                "categories": categories,
                "selected_role": selected_role
            })

        # -------------------------
        # Create user
        # -------------------------
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # -------------------------
        # Update auto-created profile
        # -------------------------
        profile = user.profile
        profile.role = role
        profile.phone = phone
        profile.profile_picture = profile_picture
        profile.category = category
        profile.save()

        # -------------------------
        # Create address (optional)
        # -------------------------
        if street or city or pincode:
            address = Address.objects.create(
                street=street,
                city=city,
                pincode=pincode
            )
            profile.address = address
            profile.save()

        messages.success(request, "Registration successful. Please log in.")
        return redirect("login")

    return render(request, "manage_user/sign_up.html", {
        "categories": categories,
        "selected_role": selected_role
    })


# =========================
# LOGOUT
# =========================
@never_cache
def logout_view(request):
    logout(request)
    return redirect("login")


# =========================
# SAVE LOCATION (AJAX)
# =========================
@login_required
def save_location(request):
    if request.method == "POST":
        data = json.loads(request.body)

        latitude = data.get("latitude")
        longitude = data.get("longitude")

        profile = Profile.objects.get(user=request.user)
        profile.latitude = latitude
        profile.longitude = longitude
        profile.save()

        return JsonResponse({"status": "success"})

    return JsonResponse({"status": "error"}, status=400)