"""
Models Gợi Ý Sản Phẩm cho ElectroShop
"""
from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product


class UserActivity(models.Model):
    """
    Theo dõi hoạt động người dùng
    """

    # Các loại hoạt động được theo dõi
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
        # Index để tối ưu query
        indexes = [
            models.Index(fields=['user', 'activity_type']),
            models.Index(fields=['product', 'activity_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['session_id']),
        ]

    def __str__(self):
        """Hiển thị thông tin hoạt động"""
        user_str = self.user.username if self.user else f'Session:{self.session_id[:8]}'
        return f"{user_str} - {self.get_activity_type_display()}"


class ProductSimilarity(models.Model):
    """
    Lưu trữ độ tương đồng giữa các sản phẩm
    """
    # Sản phẩm gốc
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='similarities',
        verbose_name='Sản phẩm'
    )

    # Sản phẩm tương tự
    similar_product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='similar_to',
        verbose_name='Sản phẩm tương tự'
    )

    # Điểm tương đồng (0.0 - 1.0)
    score = models.FloatField(
        verbose_name='Điểm tương đồng',
        help_text='Giá trị từ 0.0 (không tương đồng) đến 1.0 (rất tương đồng)'
    )

    # Thời gian cập nhật
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Cập nhật lúc'
    )

    class Meta:
        verbose_name = 'Độ tương đồng sản phẩm'
        verbose_name_plural = 'Độ tương đồng sản phẩm'
        # Đảm bảo không có cặp trùng lặp
        unique_together = ['product', 'similar_product']
        ordering = ['-score']

    def __str__(self):
        """Hiển thị cặp sản phẩm tương đồng"""
        return f"{self.product.name} ~ {self.similar_product.name} ({self.score:.2f})"


class FrequentlyBoughtTogether(models.Model):
    """
    Lưu trữ sản phẩm thường được mua cùng nhau
    """
    # Sản phẩm chính
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='bought_together',
        verbose_name='Sản phẩm'
    )

    # Sản phẩm thường mua cùng
    related_product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='bought_with',
        verbose_name='Sản phẩm mua kèm'
    )

    # Số lần mua cùng
    count = models.IntegerField(
        default=0,
        verbose_name='Số lần mua cùng',
        help_text='Số lần 2 sản phẩm xuất hiện trong cùng đơn hàng'
    )

    # Thời gian cập nhật
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Cập nhật lúc'
    )

    class Meta:
        verbose_name = 'Sản phẩm mua kèm'
        verbose_name_plural = 'Sản phẩm mua kèm'
        # Đảm bảo không có cặp trùng lặp
        unique_together = ['product', 'related_product']
        ordering = ['-count']

    def __str__(self):
        """Hiển thị cặp sản phẩm mua cùng"""
        return f"{self.product.name} + {self.related_product.name} ({self.count} lần)"
