from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Initialize the profile with the user's email to avoid creating
        # multiple profiles with an empty-string email (unique constraint).
        Profile.objects.create(user=instance, email=getattr(instance, 'email', ''))


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
