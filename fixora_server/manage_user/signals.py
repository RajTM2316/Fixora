from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, Address

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        address = Address.objects.create(
            street="",
            city="",
            pincode="000000"
        )

        Profile.objects.create(
            user=instance,
            role="customer",
            phone="0000000000",
            address=address
        )
