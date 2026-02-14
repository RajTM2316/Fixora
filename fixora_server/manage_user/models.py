from django.db import models
from django.contrib.auth.models import User


class Address(models.Model):
    street = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return f"{self.city or 'City'} - {self.pincode or '000000'}"


class Profile(models.Model):
    ROLE_CHOICES = [
        ("customer", "Customer"),
        ("provider", "Service Provider"),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # MUST HAVE DEFAULT (Fixes IntegrityError)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="customer"
    )

    profile_picture = models.ImageField(upload_to="profile_pictures/",default="profile_images/default.png", null=True, blank=True)
    phone = models.CharField(
        max_length=15,
        null=True,
        blank=True
    )

    address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.user.username
