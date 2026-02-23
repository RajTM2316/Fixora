from django.db import models
from manage_user.models import Profile


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to="category_images/", default="category_images/default.jpg", null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Service(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class ProviderService(models.Model):
    provider = models.ForeignKey(Profile, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.provider.user.username} - {self.service.name}"


class ServiceRequest(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("ACCEPTED", "Accepted"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    customer = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="requests")
    provider_service = models.ForeignKey(ProviderService, on_delete=models.CASCADE)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    request_date = models.DateTimeField(auto_now_add=True)

    address_text = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Request by {self.customer.user.username}"


class ServiceRequestImage(models.Model):
    request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="problem_photos/", null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for Request {self.request.id}"
    
from django.db.models.signals import post_save
from django.dispatch import receiver
from chat.models import Conversation


@receiver(post_save, sender=ServiceRequest)
def create_conversation(sender, instance, created, **kwargs):
    if created:
        Conversation.objects.create(service_request=instance)
