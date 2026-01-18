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
        ('zalopay', 'Ví ZaloPay'),
        ('card', 'Thẻ Visa/Mastercard/JCB'),
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
        return f"Đơn hàng #{self.order_number} - {self.user.username if self.user else 'Guest'}"

    @classmethod
    def generate_order_number(cls):
        """Tạo mã đơn hàng unique"""
        import uuid
        from datetime import datetime
        date_str = datetime.now().strftime('%Y%m%d')
        unique_id = uuid.uuid4().hex[:6].upper()
        return f"DH{date_str}{unique_id}"

    def calculate_total(self):
        """Tính tổng tiền đơn hàng"""
        self.subtotal = sum(item.total_price for item in self.items.all())
        self.total = self.subtotal + self.shipping_fee - self.discount
        self.save(update_fields=['subtotal', 'total'])

    def can_cancel(self):
        """Kiểm tra có thể hủy đơn không"""
        return self.status in ['pending', 'confirmed']

    # Định nghĩa luồng trạng thái hợp lệ cho COD
    VALID_STATUS_TRANSITIONS_COD = {
        'pending': ['confirmed', 'cancelled'],
        'confirmed': ['processing', 'cancelled'],
        'processing': ['shipping', 'cancelled'],
        'shipping': ['delivered', 'cancelled'],
        'delivered': ['completed', 'refunded'],
        'completed': ['refunded'],
        'cancelled': [],
        'refunded': [],
    }

    # Luồng trạng thái cho thanh toán online (bỏ qua delivered)
    VALID_STATUS_TRANSITIONS_ONLINE = {
        'pending': ['confirmed', 'cancelled'],
        'confirmed': ['processing', 'cancelled'],
        'processing': ['shipping', 'cancelled'],
        'shipping': ['completed', 'cancelled'],  # Bỏ qua delivered, nhảy thẳng completed
        'completed': ['refunded'],
        'cancelled': [],
        'refunded': [],
    }

    def _get_valid_transitions(self):
        """Lấy luồng trạng thái phù hợp với phương thức thanh toán"""
        if self.payment_method == 'cod':
            return self.VALID_STATUS_TRANSITIONS_COD
        else:
            return self.VALID_STATUS_TRANSITIONS_ONLINE

    def can_transition_to(self, new_status):
        """Kiểm tra có thể chuyển sang trạng thái mới không"""
        transitions = self._get_valid_transitions()
        allowed = transitions.get(self.status, [])
        return new_status in allowed

    def get_allowed_transitions(self):
        """Lấy danh sách trạng thái có thể chuyển đến"""
        transitions = self._get_valid_transitions()
        allowed_codes = transitions.get(self.status, [])
        return [(code, label) for code, label in self.STATUS_CHOICES if code in allowed_codes]

    def transition_to(self, new_status, note=''):
        """
        Chuyển đơn hàng sang trạng thái mới với validation
        
        Returns:
            tuple: (success: bool, message: str)
        """
        if not self.can_transition_to(new_status):
            current_label = dict(self.STATUS_CHOICES).get(self.status, self.status)
            new_label = dict(self.STATUS_CHOICES).get(new_status, new_status)
            return False, f'Không thể chuyển từ "{current_label}" sang "{new_label}"'

        old_status = self.status
        self.status = new_status

        # Tự động cập nhật payment_status
        if new_status == 'completed':
            self.payment_status = 'paid'
            # Cập nhật sold_count cho FlashSale
            self._update_flash_sale_sold_count()
        elif new_status == 'refunded':
            self.payment_status = 'refunded'
        elif new_status == 'cancelled' and self.payment_status == 'paid':
            self.payment_status = 'refunded'

        self.save()

        # Tạo lịch sử
        OrderHistory.objects.create(
            order=self,
            status=new_status,
            note=note
        )

        # Tạo thông báo cho người dùng
        self._send_status_notification(old_status)

        old_label = dict(self.STATUS_CHOICES).get(old_status, old_status)
        new_label = dict(self.STATUS_CHOICES).get(new_status, new_status)
        return True, f'Đã chuyển từ "{old_label}" sang "{new_label}"'

    def _send_status_notification(self, old_status=None):
        """Gửi thông báo khi trạng thái đơn hàng thay đổi"""
        if not self.user:
            return
        try:
            from apps.notifications.services.notification_service import NotificationService
            service = NotificationService()
            service.notify_order_status_change(self, old_status)
        except Exception:
            pass

    def _update_flash_sale_sold_count(self):
        """Cập nhật số lượng đã bán cho Flash Sale khi đơn hàng hoàn thành"""
        from apps.promotions.models import FlashSale
        from django.utils import timezone
        from django.db.models import F

        now = timezone.now()

        for item in self.items.all():
            if item.product:
                # Tìm Flash Sale đang hoạt động cho sản phẩm này
                flash_sale = FlashSale.objects.filter(
                    product=item.product,
                    is_active=True,
                    start_time__lte=now,
                    end_time__gte=now
                ).first()

                if flash_sale:
                    # Tăng sold_count
                    FlashSale.objects.filter(pk=flash_sale.pk).update(
                        sold_count=F('sold_count') + item.quantity
                    )


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
    note = models.TextField(blank=True, verbose_name='Ghi chú')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Lịch sử đơn hàng'
        verbose_name_plural = 'Lịch sử đơn hàng'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order.order_number} - {self.status}"

    def get_status_display(self):
        """Lấy label hiển thị của trạng thái"""
        status_dict = dict(Order.STATUS_CHOICES)
        return status_dict.get(self.status, self.status)
