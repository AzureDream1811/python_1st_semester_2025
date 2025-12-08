from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product

class Order(models.Model):
    """Model đơn hàng"""
    
    STATUS_CHOICES = [
        ('pending', 'Chờ xác nhận'),
        ('confirmed', 'Đã xác nhận'),
        ('processing', 'Đang xử lý'),
        ('shipping', 'Đang giao hàng'),
        ('delivered', 'Đã giao hàng'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Đã hủy'),
        ('refunded', 'Đã hoàn tiền'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Chờ thanh toán'),
        ('paid', 'Đã thanh toán'),
        ('failed', 'Thanh toán thất bại'),
        ('refunded', 'Đã hoàn tiền'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Thanh toán khi nhận hàng (COD)'),
        ('bank_transfer', 'Chuyển khoản ngân hàng'),
        ('momo', 'Ví MoMo'),
        ('vnpay', 'VNPay'),
    ]
    
    # Mã đơn hàng
    order_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        verbose_name='Mã đơn hàng'
    )
    
    # Người đặt
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name='Khách hàng'
    )
    
    # Thông tin giao hàng
    full_name = models.CharField(max_length=100, verbose_name='Họ tên người nhận')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=15, verbose_name='Số điện thoại')
    address = models.CharField(max_length=255, verbose_name='Địa chỉ')
    ward = models.CharField(max_length=100, blank=True, verbose_name='Phường/Xã')
    district = models.CharField(max_length=100, verbose_name='Quận/Huyện')
    city = models.CharField(max_length=100, verbose_name='Tỉnh/Thành phố')
    
    # Ghi chú
    note = models.TextField(blank=True, verbose_name='Ghi chú')
    
    # Thanh toán
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='cod',
        verbose_name='Phương thức thanh toán'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        verbose_name='Trạng thái thanh toán'
    )
    
    # Tổng tiền
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        verbose_name='Tiền hàng'
    )
    shipping_fee = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        verbose_name='Phí vận chuyển'
    )
    discount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        verbose_name='Giảm giá'
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        verbose_name='Tổng thanh toán'
    )
    
    # Trạng thái
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Trạng thái'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày đặt')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Cập nhật')
    
    class Meta:
        verbose_name = 'Đơn hàng'
        verbose_name_plural = 'Đơn hàng'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Đơn hàng #{self.order_number} - {self.user.username}"

    def calculate_total(self):
        """Tính tổng tiền đơn hàng"""
        self.subtotal = sum(item.total_price for item in self.items.all())
        self.total = self.subtotal + self.shipping_fee - self.discount
        self.save(update_fields=['subtotal', 'total'])
    
    def can_cancel(self):
        """Kiểm tra có thể hủy đơn không"""
        return self.status in ['pending', 'confirmed']

class OrderItem(models.Model):
    """Model chi tiết đơn hàng"""
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Đơn hàng'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        related_name='order_items',
        verbose_name='Sản phẩm'
    )
    
    # Lưu thông tin sản phẩm tại thời điểm đặt
    product_name = models.CharField(max_length=255, verbose_name='Tên sản phẩm')
    product_image = models.CharField(max_length=255, blank=True, verbose_name='Hình ảnh')
    
    price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name='Đơn giá'
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name='Số lượng')

    class Meta:
        verbose_name = 'Chi tiết đơn hàng'
        verbose_name_plural = 'Chi tiết đơn hàng'
    
    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
    
    @property
    def total_price(self):
        """Thành tiền"""
        return self.price * self.quantity


class OrderHistory(models.Model):
    """Model lịch sử đơn hàng"""
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name='Đơn hàng'
    )
    status = models.CharField(max_length=20, verbose_name='Trạng thái')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Lịch sử đơn hàng'
        verbose_name_plural = 'Lịch sử đơn hàng'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order.order_number} - {self.status}"