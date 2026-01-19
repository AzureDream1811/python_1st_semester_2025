"""
Notification Models for ElectroShop
Handles realtime notifications and push subscriptions
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Notification(models.Model):
    """Model for storing user notifications"""

    NOTIFICATION_TYPES = [
        ('order', 'Đơn hàng'),
        ('promotion', 'Khuyến mãi'),
        ('wishlist', 'Wishlist'),
        ('system', 'Hệ thống'),
        ('chat', 'Chat'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Người dùng'
    )

    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPES,
        verbose_name='Loại thông báo'
    )

    title = models.CharField(max_length=200, verbose_name='Tiêu đề')
    message = models.TextField(verbose_name='Nội dung')
    data = models.JSONField(default=dict, blank=True, verbose_name='Dữ liệu bổ sung')
    url = models.CharField(max_length=500, blank=True, verbose_name='Đường dẫn')

    is_read = models.BooleanField(default=False, verbose_name='Đã đọc')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    read_at = models.DateTimeField(null=True, blank=True, verbose_name='Ngày đọc')

    class Meta:
        verbose_name = 'Thông báo'
        verbose_name_plural = 'Thông báo'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', 'notification_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])


class PushSubscription(models.Model):
    """Model for storing push notification subscriptions"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='push_subscriptions',
        verbose_name='Người dùng'
    )

    endpoint = models.CharField(max_length=500, verbose_name='Endpoint')
    p256dh = models.CharField(max_length=200, verbose_name='P256DH Key')
    auth = models.CharField(max_length=100, verbose_name='Auth Key')

    is_active = models.BooleanField(default=True, verbose_name='Đang hoạt động')
    user_agent = models.CharField(max_length=500, blank=True, verbose_name='User Agent')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày đăng ký')
    last_used = models.DateTimeField(auto_now=True, verbose_name='Lần sử dụng cuối')

    class Meta:
        verbose_name = 'Đăng ký Push'
        verbose_name_plural = 'Đăng ký Push'
        unique_together = ['user', 'endpoint']
        indexes = [
            models.Index(fields=['user', 'is_active']),
        ]

    def __str__(self):
        return f"{self.user.username} - Push Subscription"


class NotificationPreference(models.Model):
    """User preferences for notifications"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preferences',
        verbose_name='Người dùng'
    )

    # Email Notifications
    email_order_updates = models.BooleanField(default=True, verbose_name='Email cập nhật đơn hàng')
    email_promotions = models.BooleanField(default=True, verbose_name='Email khuyến mãi')
    email_wishlist = models.BooleanField(default=True, verbose_name='Email wishlist giảm giá')
    email_newsletter = models.BooleanField(default=False, verbose_name='Email bản tin')
    email_account = models.BooleanField(default=True, verbose_name='Email tài khoản (bảo mật)')

    # Push Notifications
    push_order_updates = models.BooleanField(default=True, verbose_name='Push cập nhật đơn hàng')
    push_promotions = models.BooleanField(default=True, verbose_name='Push khuyến mãi')
    push_wishlist = models.BooleanField(default=True, verbose_name='Push wishlist giảm giá')
    push_chat = models.BooleanField(default=True, verbose_name='Push chat hỗ trợ')
    push_flash_sale = models.BooleanField(default=True, verbose_name='Push flash sale')
    push_delivery = models.BooleanField(default=True, verbose_name='Push giao hàng')

    # SMS Notifications
    sms_order_confirmation = models.BooleanField(default=False, verbose_name='SMS xác nhận đơn hàng')
    sms_delivery = models.BooleanField(default=False, verbose_name='SMS giao hàng')

    updated_at = models.DateTimeField(auto_now=True, verbose_name='Cập nhật lần cuối')

    class Meta:
        verbose_name = 'Tùy chọn thông báo'
        verbose_name_plural = 'Tùy chọn thông báo'

    def __str__(self):
        return f"{self.user.username} - Notification Preferences"
