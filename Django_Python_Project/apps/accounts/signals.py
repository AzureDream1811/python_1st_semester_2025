from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Tạo profile với email từ user (tránh lỗi unique constraint)
        Profile.objects.create(
            user=instance,
            email=instance.email or f'{instance.username}@placeholder.local'
        )


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        # Đồng bộ email từ user sang profile
        if instance.email and instance.profile.email != instance.email:
            instance.profile.email = instance.email
        instance.profile.save()
