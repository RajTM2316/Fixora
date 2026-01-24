from django.db import models
from django.contrib.auth.models import User


class Address(models.Model):
    street = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.city} - {self.pincode}"


class Profile(models.Model):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('provider', 'Service Provider'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # ⬇️ MAKE THESE SAFE FOR SIGNAL
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        blank=True
    )

    phone = models.CharField(
        max_length=15,
        blank=True
    )

    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.user.username
