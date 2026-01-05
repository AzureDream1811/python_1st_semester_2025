"""
Models Khuyến Mãi cho ElectroShop
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from apps.products.models import Product


class Voucher(models.Model):
    """
    Model Voucher/Mã giảm giá

    Hỗ trợ 2 loại giảm giá:
    - percentage: Giảm theo phần trăm (VD: 10% tổng đơn)
    - fixed: Giảm số tiền cố định (VD: 50.000đ)
    """

    # Các loại giảm giá được hỗ trợ
    DISCOUNT_TYPES = [
        ('percentage', 'Phần trăm'),  # Giảm theo % tổng đơn
        ('fixed', 'Số tiền cố định'),  # Giảm số tiền cố định
    ]

    # Thông tin cơ bản của voucher
    code = models.CharField(max_length=50, unique=True, verbose_name='Mã voucher')
    name = models.CharField(max_length=200, verbose_name='Tên voucher')
    description = models.TextField(blank=True, verbose_name='Mô tả')

    # Cấu hình giảm giá
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES, verbose_name='Loại giảm giá')
    discount_value = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Giá trị giảm')
    min_order_value = models.DecimalField(max_digits=12, decimal_places=2, default=0,
                                          verbose_name='Giá trị đơn tối thiểu')
    max_discount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True,
                                       verbose_name='Giảm tối đa')

    # Giới hạn sử dụng
    usage_limit = models.IntegerField(default=0, verbose_name='Giới hạn sử dụng (0=không giới hạn)')
    used_count = models.IntegerField(default=0, verbose_name='Số lần đã dùng')
    usage_limit_per_user = models.IntegerField(default=1, verbose_name='Giới hạn/người dùng')

    # Thời gian hiệu lực
    valid_from = models.DateTimeField(verbose_name='Có hiệu lực từ')
    valid_until = models.DateTimeField(verbose_name='Hết hạn')

    # Trạng thái
    is_active = models.BooleanField(default=True, verbose_name='Đang hoạt động')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')

    class Meta:
        verbose_name = 'Voucher'
        verbose_name_plural = 'Vouchers'
        ordering = ['-created_at']

    def __str__(self):
        """Hiển thị mã và tên voucher"""
        return f"{self.code} - {self.name}"

    def is_valid(self):
        """
        Kiểm tra voucher có còn hiệu lực không

        Điều kiện hợp lệ:
        - Voucher đang active
        - Thời gian hiện tại nằm trong khoảng valid_from -> valid_until
        - Chưa vượt quá giới hạn sử dụng (nếu có)
        """
        now = timezone.now()

        # Kiểm tra trạng thái active
        if not self.is_active:
            return False

        # Kiểm tra thời gian hiệu lực
        if now < self.valid_from or now > self.valid_until:
            return False

        # Kiểm tra giới hạn sử dụng (0 = không giới hạn)
        if self.usage_limit > 0 and self.used_count >= self.usage_limit:
            return False

        return True


class VoucherUsage(models.Model):
    """
    Model theo dõi lịch sử sử dụng Voucher

    Ghi lại thông tin mỗi lần voucher được sử dụng:
    - Ai sử dụng (user)
    - Cho đơn hàng nào (order)
    - Số tiền được giảm (discount_amount)
    - Thời điểm sử dụng (used_at)

    Dùng để:
    - Kiểm tra giới hạn sử dụng mỗi người
    - Thống kê hiệu quả voucher
    - Báo cáo khuyến mãi
    """
    # Liên kết với voucher
    voucher = models.ForeignKey(
        Voucher,
        on_delete=models.CASCADE,
        related_name='usages',
        verbose_name='Voucher'
    )

    # Người sử dụng
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Người dùng'
    )

    # Đơn hàng áp dụng
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        verbose_name='Đơn hàng'
    )

    # Số tiền được giảm
    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Số tiền giảm'
    )

    # Thời điểm sử dụng
    used_at = models.DateTimeField(auto_now_add=True, verbose_name='Thời điểm sử dụng')

    class Meta:
        verbose_name = 'Lịch sử sử dụng voucher'
        verbose_name_plural = 'Lịch sử sử dụng voucher'
        ordering = ['-used_at']

    def __str__(self):
        """Hiển thị thông tin sử dụng voucher"""
        return f"{self.user.username} - {self.voucher.code} - {self.discount_amount:,.0f}đ"


class ComboDeal(models.Model):
    """
    Model Combo Deal - Khuyến mãi khi mua combo sản phẩm

    Cho phép tạo các combo khuyến mãi:
    - Mua sản phẩm A + B + C được giảm X%

    Tự động áp dụng khi giỏ hàng chứa đủ các sản phẩm trong combo
    """
    # Thông tin combo
    name = models.CharField(max_length=200, verbose_name='Tên combo')
    description = models.TextField(blank=True, verbose_name='Mô tả')

    # Danh sách sản phẩm trong combo
    products = models.ManyToManyField(
        Product,
        related_name='combo_deals',
        verbose_name='Sản phẩm trong combo'
    )

    # Cấu hình giảm giá
    discount_type = models.CharField(
        max_length=20,
        choices=Voucher.DISCOUNT_TYPES,
        verbose_name='Loại giảm giá'
    )
    discount_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Giá trị giảm'
    )

    # Thời gian hiệu lực
    valid_from = models.DateTimeField(verbose_name='Có hiệu lực từ')
    valid_until = models.DateTimeField(verbose_name='Hết hạn')

    # Trạng thái
    is_active = models.BooleanField(default=True, verbose_name='Đang hoạt động')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')

    class Meta:
        verbose_name = 'Combo Deal'
        verbose_name_plural = 'Combo Deals'
        ordering = ['-created_at']

    def __str__(self):
        """Hiển thị tên combo"""
        return self.name

    def is_valid(self):
        """
        Kiểm tra combo có còn hiệu lực không
        """
        now = timezone.now()
        return (
                self.is_active and
                self.valid_from <= now <= self.valid_until
        )


class FlashSale(models.Model):
    """
    Model Flash Sale - Giảm giá sốc theo thời gian

    Chương trình giảm giá đặc biệt với:
    - Thời gian giới hạn (VD: 2 tiếng)
    - Số lượng giới hạn (VD: chỉ 50 sản phẩm)
    - Giá sale đặc biệt
    """
    # Sản phẩm flash sale
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='flash_sales',
        verbose_name='Sản phẩm'
    )

    # Giá flash sale (thay thế giá gốc trong thời gian sale)
    sale_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Giá flash sale'
    )

    # Giới hạn số lượng
    quantity_limit = models.IntegerField(verbose_name='Số lượng giới hạn')
    sold_count = models.IntegerField(default=0, verbose_name='Đã bán')

    # Thời gian diễn ra
    start_time = models.DateTimeField(verbose_name='Bắt đầu')
    end_time = models.DateTimeField(verbose_name='Kết thúc')

    # Trạng thái
    is_active = models.BooleanField(default=True, verbose_name='Đang hoạt động')

    class Meta:
        verbose_name = 'Flash Sale'
        verbose_name_plural = 'Flash Sales'
        ordering = ['-start_time']

    def __str__(self):
        """Hiển thị tên sản phẩm flash sale"""
        return f"Flash Sale: {self.product.name}"

    def is_available(self):
        """
        Kiểm tra flash sale có còn khả dụng không

        Điều kiện khả dụng:
        - Flash sale đang active
        - Thời gian hiện tại nằm trong khoảng start_time -> end_time
        - Số lượng đã bán chưa vượt quá giới hạn
        """
        now = timezone.now()
        return (
                self.is_active and
                self.start_time <= now <= self.end_time and
                self.sold_count < self.quantity_limit
        )

    def remaining_quantity(self):
        """
        Tính số lượng còn lại
        """
        return max(0, self.quantity_limit - self.sold_count)

    def discount_percentage(self):
        """
        Tính phần trăm giảm giá so với giá gốc
        """
        if self.product.price > 0:
            discount = ((self.product.price - self.sale_price) / self.product.price) * 100
            return int(discount)
        return 0
