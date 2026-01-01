"""
Analytics Models for ElectroShop
User tracking, funnel events, search logs
"""
from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product


class FunnelEvent(models.Model):
    """Track conversion funnel events"""

    FUNNEL_STEPS = [
        ('view_product', 'Xem sản phẩm'),
        ('add_to_cart', 'Thêm vào giỏ'),
        ('view_cart', 'Xem giỏ hàng'),
        ('checkout', 'Thanh toán'),
        ('complete', 'Hoàn thành'),
    ]

    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    session_id = models.CharField(max_length=100)
    step = models.CharField(max_length=50, choices=FUNNEL_STEPS)
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Sự kiện Funnel'
        verbose_name_plural = 'Sự kiện Funnel'
        indexes = [
            models.Index(fields=['session_id', 'step']),
            models.Index(fields=['created_at']),
        ]


class SearchLog(models.Model):
    """Track search queries"""
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    query = models.CharField(max_length=200, verbose_name='Từ khóa')
    results_count = models.IntegerField(default=0, verbose_name='Số kết quả')
    clicked_product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Lịch sử tìm kiếm'
        verbose_name_plural = 'Lịch sử tìm kiếm'
        ordering = ['-created_at']


class DailyStats(models.Model):
    """Pre-aggregated daily statistics"""
    date = models.DateField(unique=True)
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_orders = models.IntegerField(default=0)
    total_visitors = models.IntegerField(default=0)
    total_page_views = models.IntegerField(default=0)
    conversion_rate = models.FloatField(default=0)
    avg_order_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Thống kê ngày'
        verbose_name_plural = 'Thống kê ngày'
        ordering = ['-date']
