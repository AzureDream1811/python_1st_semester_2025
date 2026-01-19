from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        email_value = (instance.email or instance.username or '').strip().lower()
        if not email_value:
            email_value = f'user-{instance.pk}@example.invalid'
        Profile.objects.create(user=instance, email=email_value)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
