from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Profile
from django.contrib.auth.models import User
from .models import Address

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
                    return redirect("/provider-dashboard/")
                else:
                    return redirect("/")  # customer home
            else:
                messages.error(request, "Incorrect role selected.")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "manage_user/login.html")

from django.http import HttpResponse

def signup_view(request):
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

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, "manage_user/sign_up.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return render(request, "manage_user/sign_up.html")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        profile = Profile.objects.create(
            user=user,
            role=role,
            phone=phone,
            profile_picture=profile_picture
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

    return render(request, "manage_user/sign_up.html")


