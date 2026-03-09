from django.db import models
from django.contrib.auth.models import User
from manage_service.models import Category
from django.db.models.signals import post_save
from django.dispatch import receiver

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

    category = models.ForeignKey(
        "manage_service.Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="providers"
    )

    #feedback and rating
    average_rating = models.FloatField(default=0)
    total_reviews = models.IntegerField(default=0)
    #For Live-Location Tracking
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return self.user.username




@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
