"""
Payment Models for ElectroShop
Payment transactions and refunds
"""
from django.db import models
from apps.orders.models import Order


class PaymentTransaction(models.Model):
    """Payment transaction model"""

    PAYMENT_METHODS = [
        ('cod', 'Thanh toán khi nhận hàng'),
        ('card', 'Thanh toán bằng thẻ'),
        ('vnpay', 'VNPay'),
        ('momo', 'MoMo'),
        ('zalopay', 'ZaloPay'),
        ('bank_transfer', 'Chuyển khoản'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Chờ xử lý'),
        ('processing', 'Đang xử lý'),
        ('success', 'Thành công'),
        ('failed', 'Thất bại'),
        ('cancelled', 'Đã hủy'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payment_transactions',
                              verbose_name='Đơn hàng')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, verbose_name='Phương thức')
    transaction_id = models.CharField(max_length=100, unique=True, verbose_name='Mã giao dịch')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Số tiền')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Trạng thái')
    response_code = models.CharField(max_length=50, blank=True, verbose_name='Mã phản hồi')
    response_message = models.TextField(blank=True, verbose_name='Thông báo')
    response_data = models.JSONField(default=dict, blank=True, verbose_name='Dữ liệu phản hồi')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Cập nhật')

    class Meta:
        verbose_name = 'Giao dịch thanh toán'
        verbose_name_plural = 'Giao dịch thanh toán'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_id} - {self.amount:,.0f}đ ({self.status})"


class Refund(models.Model):
    """Refund model"""

    STATUS_CHOICES = [
        ('pending', 'Chờ xử lý'),
        ('processing', 'Đang xử lý'),
        ('completed', 'Hoàn thành'),
        ('failed', 'Thất bại'),
    ]

    payment = models.ForeignKey(PaymentTransaction, on_delete=models.CASCADE, related_name='refunds',
                                verbose_name='Giao dịch gốc')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Số tiền hoàn')
    reason = models.TextField(verbose_name='Lý do')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Trạng thái')
    refund_transaction_id = models.CharField(max_length=100, blank=True, verbose_name='Mã giao dịch hoàn')
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name='Ngày xử lý')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')

    class Meta:
        verbose_name = 'Hoàn tiền'
        verbose_name_plural = 'Hoàn tiền'

    def __str__(self):
        return f"Refund {self.id} - {self.amount:,.0f}đ"


class BankAccount(models.Model):
    """Tài khoản ngân hàng nhận thanh toán"""

    BANK_CODES = [
        ('VCB', 'Vietcombank'),
        ('TCB', 'Techcombank'),
        ('MB', 'MB Bank'),
        ('ACB', 'ACB'),
        ('VPB', 'VPBank'),
        ('TPB', 'TPBank'),
        ('BIDV', 'BIDV'),
        ('VTB', 'VietinBank'),
        ('STB', 'Sacombank'),
        ('HDB', 'HDBank'),
        ('MSB', 'MSB'),
        ('OCB', 'OCB'),
        ('SHB', 'SHB'),
        ('EIB', 'Eximbank'),
        ('NAB', 'Nam A Bank'),
    ]

    bank_code = models.CharField(
        max_length=20,
        choices=BANK_CODES,
        verbose_name='Mã ngân hàng'
    )
    bank_name = models.CharField(max_length=100, verbose_name='Tên ngân hàng')
    account_number = models.CharField(max_length=30, verbose_name='Số tài khoản')
    account_name = models.CharField(max_length=100, verbose_name='Tên tài khoản')
    branch = models.CharField(max_length=200, blank=True, verbose_name='Chi nhánh')
    is_active = models.BooleanField(default=True, verbose_name='Đang hoạt động')
    is_default = models.BooleanField(default=False, verbose_name='Mặc định')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')

    class Meta:
        verbose_name = 'Tài khoản ngân hàng'
        verbose_name_plural = 'Tài khoản ngân hàng'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.bank_name} - {self.account_number} ({self.account_name})"

    def save(self, *args, **kwargs):
        """Override save để đảm bảo chỉ có 1 tài khoản mặc định"""
        if self.is_default:
            BankAccount.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class EWalletAccount(models.Model):
    """Tài khoản ví điện tử nhận thanh toán"""

    WALLET_TYPES = [
        ('momo', 'MoMo'),
        ('zalopay', 'ZaloPay'),
    ]

    wallet_type = models.CharField(
        max_length=20,
        choices=WALLET_TYPES,
        verbose_name='Loại ví'
    )
    wallet_id = models.CharField(
        max_length=50,
        verbose_name='ID ví / Số điện thoại'
    )
    wallet_name = models.CharField(
        max_length=100,
        verbose_name='Tên chủ ví'
    )
    is_active = models.BooleanField(default=True, verbose_name='Đang hoạt động')
    is_default = models.BooleanField(default=False, verbose_name='Mặc định')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')

    class Meta:
        verbose_name = 'Ví điện tử'
        verbose_name_plural = 'Ví điện tử'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.get_wallet_type_display()} - {self.wallet_id} ({self.wallet_name})"

    def save(self, *args, **kwargs):
        """Override save để đảm bảo chỉ có 1 ví mặc định cho mỗi loại"""
        if self.is_default:
            EWalletAccount.objects.filter(
                wallet_type=self.wallet_type,
                is_default=True
            ).update(is_default=False)
        super().save(*args, **kwargs)
