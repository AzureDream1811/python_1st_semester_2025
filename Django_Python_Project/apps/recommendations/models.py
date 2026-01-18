"""
Models Gợi Ý Sản Phẩm cho ElectroShop
=====================================

Module này định nghĩa các models liên quan đến hệ thống gợi ý sản phẩm:
- UserActivity: Theo dõi hoạt động người dùng (xem, mua, thêm giỏ...)
- ProductSimilarity: Lưu trữ độ tương đồng giữa các sản phẩm
- FrequentlyBoughtTogether: Sản phẩm thường được mua cùng nhau

Dữ liệu từ các models này được sử dụng bởi AI/ML để:
- Gợi ý sản phẩm cá nhân hóa
- Hiển thị "Sản phẩm tương tự"
- Hiển thị "Thường mua cùng"
- Phân tích xu hướng mua sắm

Tác giả: ElectroShop Team
"""
from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product


class UserActivity(models.Model):
    """
    Model theo dõi hoạt động người dùng
    
    Ghi lại mọi tương tác của người dùng với sản phẩm:
    - Xem sản phẩm
    - Thêm vào giỏ hàng
    - Mua hàng
    - Thêm vào wishlist
    - Tìm kiếm
    
    Dữ liệu này được sử dụng để:
    - Tạo gợi ý cá nhân hóa
    - Phân tích hành vi người dùng
    - Tính toán sản phẩm trending
    """

    # Các loại hoạt động được theo dõi
    ACTIVITY_TYPES = [
        ('view', 'Xem sản phẩm'),  # Người dùng xem chi tiết sản phẩm
        ('add_to_cart', 'Thêm vào giỏ'),  # Thêm sản phẩm vào giỏ hàng
        ('purchase', 'Mua hàng'),  # Hoàn tất mua hàng
        ('wishlist', 'Thêm wishlist'),  # Thêm vào danh sách yêu thích
        ('search', 'Tìm kiếm'),  # Tìm kiếm sản phẩm
    ]

    # Người dùng thực hiện hoạt động (có thể null nếu chưa đăng nhập)
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Người dùng',
        related_name='activities'
    )

    # Session ID để theo dõi người dùng chưa đăng nhập
    session_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Session ID',
        help_text='Dùng để theo dõi người dùng chưa đăng nhập'
    )

    # Loại hoạt động
    activity_type = models.CharField(
        max_length=50,
        choices=ACTIVITY_TYPES,
        verbose_name='Loại hoạt động'
    )

    # Sản phẩm liên quan (có thể null nếu là hoạt động tìm kiếm)
    product = models.ForeignKey(
        Product,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Sản phẩm',
        related_name='user_activities'
    )

    # Từ khóa tìm kiếm (chỉ dùng cho activity_type='search')
    search_query = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Từ khóa tìm kiếm'
    )

    # Metadata bổ sung (JSON)
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Metadata',
        help_text='Dữ liệu bổ sung như: thời gian xem, nguồn truy cập...'
    )

    # Thời gian hoạt động
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Thời gian'
    )

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
    Model lưu trữ độ tương đồng giữa các sản phẩm
    
    Dữ liệu được tính toán trước (pre-computed) bởi thuật toán ML
    dựa trên:
    - Cùng danh mục
    - Cùng thương hiệu
    - Thuộc tính tương tự (giá, specs...)
    - Hành vi người dùng (xem cùng, mua cùng)
    
    Được sử dụng để hiển thị "Sản phẩm tương tự" trên trang chi tiết
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
    Model lưu trữ sản phẩm thường được mua cùng nhau
    
    Dữ liệu được tính toán từ lịch sử đơn hàng:
    - Đếm số lần 2 sản phẩm xuất hiện trong cùng 1 đơn hàng
    - Cập nhật định kỳ bởi Celery task
    
    Được sử dụng để hiển thị:
    - "Thường mua cùng" trên trang chi tiết
    - Gợi ý combo khi thêm vào giỏ hàng
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
