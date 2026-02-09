from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # redirect based on role
            if hasattr(user, "profile") and user.profile.role == "provider":
                return redirect("/provider-dashboard/")
            else:
                return redirect("/")  # customer home
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "manage_user/login.html")
