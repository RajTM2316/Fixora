from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login , logout
from django.contrib import messages
from .models import Profile
from django.contrib.auth.models import User
from .models import Address
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from manage_service.models import Category
import json

@never_cache
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        role = request.POST.get("role")  # role from toggle

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Check if profile exists and role matches
            if hasattr(user, "profile") and user.profile.role == role:
                login(request, user)

                # redirect based on role
                if role == "provider":
                    return redirect("provider_dashboard")
                else:
                    return redirect("customer_home")  # customer home
            else:
                messages.error(request, "Incorrect role selected.")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "manage_user/login.html")

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

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, "manage_user/sign_up.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return render(request, "manage_user/sign_up.html")

        if role == "provider" and not category:
            messages.error(request, "Service providers must select a category.")
            return render(request, "manage_user/sign_up.html",{
                "categories": Category.objects.all()
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        profile = Profile.objects.create(
            user=user,
            role=role,
            phone=phone,
            profile_picture=profile_picture,
            category=category
        )

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
@never_cache
def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
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
