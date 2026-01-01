"""
Recommendation Models for ElectroShop
User activity tracking and product similarity
"""
from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product


class UserActivity(models.Model):
    """Track user activities for recommendations"""

    ACTIVITY_TYPES = [
        ('view', 'Xem sản phẩm'),
        ('add_to_cart', 'Thêm vào giỏ'),
        ('purchase', 'Mua hàng'),
        ('wishlist', 'Thêm wishlist'),
        ('search', 'Tìm kiếm'),
    ]

    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Người dùng')
    session_id = models.CharField(max_length=100, blank=True, verbose_name='Session ID')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES, verbose_name='Loại hoạt động')
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Sản phẩm')
    search_query = models.CharField(max_length=200, blank=True, verbose_name='Từ khóa tìm kiếm')
    metadata = models.JSONField(default=dict, blank=True, verbose_name='Metadata')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Thời gian')

    class Meta:
        verbose_name = 'Hoạt động người dùng'
        verbose_name_plural = 'Hoạt động người dùng'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'activity_type']),
            models.Index(fields=['product', 'activity_type']),
            models.Index(fields=['created_at']),
        ]


class ProductSimilarity(models.Model):
    """Pre-computed product similarity scores"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='similarities')
    similar_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='similar_to')
    score = models.FloatField(verbose_name='Điểm tương đồng')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Độ tương đồng sản phẩm'
        verbose_name_plural = 'Độ tương đồng sản phẩm'
        unique_together = ['product', 'similar_product']


class FrequentlyBoughtTogether(models.Model):
    """Products frequently bought together"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bought_together')
    related_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bought_with')
    count = models.IntegerField(default=0, verbose_name='Số lần mua cùng')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Sản phẩm mua kèm'
        verbose_name_plural = 'Sản phẩm mua kèm'
        unique_together = ['product', 'related_product']
