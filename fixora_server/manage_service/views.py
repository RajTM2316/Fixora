# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Category
from django.contrib import messages

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

def add_category(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        image = request.FILES.get("image")
        is_active = True if request.POST.get("is_active") == "on" else False
        if Category.objects.filter(name=name).exists():
            messages.error(request, "Category with this name already exists.")
            return redirect("add_category")
        else:
            Category.objects.create(name=name, description=description, image=image, is_active=is_active)
            messages.success(request, "Category added successfully.")
            return redirect("add_category")
    return render(request, "manage_service/add_category.html")