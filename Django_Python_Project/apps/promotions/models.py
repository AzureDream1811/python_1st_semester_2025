"""
Promotion Models for ElectroShop
Vouchers, Combo Deals, Flash Sales
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from apps.products.models import Product


class Voucher(models.Model):
    """Voucher/Coupon model"""

    DISCOUNT_TYPES = [
        ('percentage', 'Phần trăm'),
        ('fixed', 'Số tiền cố định'),
    ]

    code = models.CharField(max_length=50, unique=True, verbose_name='Mã voucher')
    name = models.CharField(max_length=200, verbose_name='Tên voucher')
    description = models.TextField(blank=True, verbose_name='Mô tả')
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES, verbose_name='Loại giảm giá')
    discount_value = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Giá trị giảm')
    min_order_value = models.DecimalField(max_digits=12, decimal_places=2, default=0,
                                          verbose_name='Giá trị đơn tối thiểu')
    max_discount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True,
                                       verbose_name='Giảm tối đa')
    usage_limit = models.IntegerField(default=0, verbose_name='Giới hạn sử dụng (0=không giới hạn)')
    used_count = models.IntegerField(default=0, verbose_name='Số lần đã dùng')
    usage_limit_per_user = models.IntegerField(default=1, verbose_name='Giới hạn/người dùng')
    valid_from = models.DateTimeField(verbose_name='Có hiệu lực từ')
    valid_until = models.DateTimeField(verbose_name='Hết hạn')
    is_active = models.BooleanField(default=True, verbose_name='Đang hoạt động')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Voucher'
        verbose_name_plural = 'Vouchers'

    def __str__(self):
        return f"{self.code} - {self.name}"

    def is_valid(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if now < self.valid_from or now > self.valid_until:
            return False
        if self.usage_limit > 0 and self.used_count >= self.usage_limit:
            return False
        return True


class VoucherUsage(models.Model):
    """Track voucher usage by users"""
    voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Lịch sử sử dụng voucher'
        verbose_name_plural = 'Lịch sử sử dụng voucher'


class ComboDeal(models.Model):
    """Combo deal model"""
    name = models.CharField(max_length=200, verbose_name='Tên combo')
    description = models.TextField(blank=True, verbose_name='Mô tả')
    products = models.ManyToManyField(Product, related_name='combo_deals', verbose_name='Sản phẩm')
    discount_type = models.CharField(max_length=20, choices=Voucher.DISCOUNT_TYPES, verbose_name='Loại giảm giá')
    discount_value = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Giá trị giảm')
    valid_from = models.DateTimeField(verbose_name='Có hiệu lực từ')
    valid_until = models.DateTimeField(verbose_name='Hết hạn')
    is_active = models.BooleanField(default=True, verbose_name='Đang hoạt động')

    class Meta:
        verbose_name = 'Combo Deal'
        verbose_name_plural = 'Combo Deals'

    def __str__(self):
        return self.name


class FlashSale(models.Model):
    """Flash sale model"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='flash_sales', verbose_name='Sản phẩm')
    sale_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Giá flash sale')
    quantity_limit = models.IntegerField(verbose_name='Số lượng giới hạn')
    sold_count = models.IntegerField(default=0, verbose_name='Đã bán')
    start_time = models.DateTimeField(verbose_name='Bắt đầu')
    end_time = models.DateTimeField(verbose_name='Kết thúc')
    is_active = models.BooleanField(default=True, verbose_name='Đang hoạt động')

    class Meta:
        verbose_name = 'Flash Sale'
        verbose_name_plural = 'Flash Sales'

    def __str__(self):
        return f"Flash Sale: {self.product.name}"

    def is_available(self):
        now = timezone.now()
        return (self.is_active and
                self.start_time <= now <= self.end_time and
                self.sold_count < self.quantity_limit)
