"""
Shipping Models for ElectroShop
Shipment tracking and carrier integration
"""
from django.db import models
from apps.orders.models import Order


class CarrierConfig(models.Model):
    """Shipping carrier configuration"""

    CARRIERS = [
        ('ghn', 'Giao Hàng Nhanh'),
        ('ghtk', 'Giao Hàng Tiết Kiệm'),
        ('viettel_post', 'Viettel Post'),
        ('vnpost', 'VN Post'),
    ]

    carrier = models.CharField(max_length=20, choices=CARRIERS, unique=True, verbose_name='Đơn vị vận chuyển')
    name = models.CharField(max_length=100, verbose_name='Tên hiển thị')
    is_active = models.BooleanField(default=True, verbose_name='Đang hoạt động')
    is_default = models.BooleanField(default=False, verbose_name='Mặc định')
    api_token = models.CharField(max_length=200, blank=True, verbose_name='API Token')
    shop_id = models.CharField(max_length=100, blank=True, verbose_name='Shop ID')
    config = models.JSONField(default=dict, blank=True, verbose_name='Cấu hình')

    class Meta:
        verbose_name = 'Cấu hình vận chuyển'
        verbose_name_plural = 'Cấu hình vận chuyển'

    def __str__(self):
        return self.name


class Shipment(models.Model):
    """Shipment model"""

    STATUS_CHOICES = [
        ('pending', 'Chờ lấy hàng'),
        ('picked_up', 'Đã lấy hàng'),
        ('in_transit', 'Đang vận chuyển'),
        ('out_for_delivery', 'Đang giao'),
        ('delivered', 'Đã giao'),
        ('failed', 'Giao thất bại'),
        ('returned', 'Hoàn hàng'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipment', verbose_name='Đơn hàng')
    carrier = models.CharField(max_length=20, choices=CarrierConfig.CARRIERS, verbose_name='Đơn vị vận chuyển')
    tracking_code = models.CharField(max_length=100, unique=True, verbose_name='Mã vận đơn')
    shipping_fee = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Phí vận chuyển')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending', verbose_name='Trạng thái')
    estimated_delivery = models.DateField(null=True, blank=True, verbose_name='Dự kiến giao')
    actual_delivery = models.DateTimeField(null=True, blank=True, verbose_name='Thực tế giao')
    weight = models.IntegerField(default=0, verbose_name='Khối lượng (gram)')
    cod_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Tiền thu hộ')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Cập nhật')

    class Meta:
        verbose_name = 'Vận đơn'
        verbose_name_plural = 'Vận đơn'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.tracking_code} - {self.order.order_number}"


class ShipmentTracking(models.Model):
    """Shipment tracking history"""
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='tracking_history',
                                 verbose_name='Vận đơn')
    status = models.CharField(max_length=100, verbose_name='Trạng thái')
    location = models.CharField(max_length=200, blank=True, verbose_name='Vị trí')
    description = models.TextField(verbose_name='Mô tả')
    timestamp = models.DateTimeField(verbose_name='Thời gian')
    raw_data = models.JSONField(default=dict, blank=True, verbose_name='Dữ liệu gốc')

    class Meta:
        verbose_name = 'Lịch sử vận chuyển'
        verbose_name_plural = 'Lịch sử vận chuyển'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.shipment.tracking_code} - {self.status}"


class ShippingRate(models.Model):
    """Pre-configured shipping rates"""
    carrier = models.CharField(max_length=20, choices=CarrierConfig.CARRIERS, verbose_name='Đơn vị')
    from_province = models.CharField(max_length=100, verbose_name='Tỉnh gửi')
    to_province = models.CharField(max_length=100, verbose_name='Tỉnh nhận')
    weight_from = models.IntegerField(verbose_name='Từ (gram)')
    weight_to = models.IntegerField(verbose_name='Đến (gram)')
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Giá')

    class Meta:
        verbose_name = 'Bảng giá vận chuyển'
        verbose_name_plural = 'Bảng giá vận chuyển'
