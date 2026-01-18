"""
Signals for Notification System
Auto-create notifications on various events
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from apps.notifications.models import NotificationPreference


@receiver(post_save, sender=User)
def create_notification_preferences(sender, instance, created, **kwargs):
    """Create notification preferences for new users"""
    if created:
        NotificationPreference.objects.get_or_create(user=instance)


# Order status change signal - will be connected in orders app
def notify_order_status_change(sender, instance, **kwargs):
    """Send notification when order status changes"""
    from apps.notifications.services import NotificationService

    # Check if status changed
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                service = NotificationService()
                service.notify_order_status_change(instance)
        except sender.DoesNotExist:
            pass


# Product price change signal - will be connected in products app
def notify_price_drop(sender, instance, **kwargs):
    """Send notification when product price drops"""
    from apps.notifications.services import NotificationService

    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            old_price = old_instance.sale_price or old_instance.price
            new_price = instance.sale_price or instance.price

            if new_price < old_price:
                service = NotificationService()
                service.notify_wishlist_price_drop(instance, old_price, new_price)
        except sender.DoesNotExist:
            pass
