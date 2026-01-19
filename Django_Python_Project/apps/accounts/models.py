from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class Profile(models.Model):
    """Custom User Model với thông tin bổ sung"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    phone_regex = RegexValidator(
        regex=r'^(0|\+84)[0-9]{9,10}$',
        message="Số điện thoại phải có định dạng: '0xxxxxxxxx' hoặc '+84xxxxxxxxx'"
    )

    email = models.EmailField(unique=True, verbose_name='Email', max_length=150)
    phone = models.CharField(
        validators=[phone_regex],
        max_length=15,
        blank=True,
        null=True,
        verbose_name='Số điện thoại'
    )
    address = models.TextField(blank=True, null=True, verbose_name='Địa chỉ')
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Ảnh đại diện'
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        verbose_name='Ngày sinh'
    )
    gender = models.CharField(max_length=10, blank=True, choices=[
        ('male', 'Nam'),
        ('female', 'Nữ'),
        ('other', 'Khác'),
    ], verbose_name='Giới tính')

    # Social login fields
    is_social_account = models.BooleanField(default=False, verbose_name='Tài khoản Social')
    social_provider = models.CharField(max_length=20, blank=True, verbose_name='Nhà cung cấp Social')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')

    class Meta:
        verbose_name = 'Hồ sơ người dùng'
        verbose_name_plural = 'Hồ sơ người dùng'

    def __str__(self):
        return f'Profile of {self.user.username}'

    def get_avatar_url(self):
        """Lấy URL avatar hoặc avatar mặc định"""
        if self.avatar:
            return self.avatar.url
        return '/static/images/default-avatar.png'


class Address(models.Model):
    """Model địa chỉ giao hàng"""

    phone_regex = RegexValidator(
        regex=r'^(0|\+84)[0-9]{9,10}$',
        message="Số điện thoại phải có định dạng: '0xxxxxxxxx' hoặc '+84xxxxxxxxx'"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name='Người dùng'
    )
    full_name = models.CharField(max_length=100, verbose_name='Họ tên người nhận')
    phone = models.CharField(
        validators=[phone_regex],
        max_length=15,
        verbose_name='Số điện thoại',
        blank=True,
        default=''
    )
    address = models.TextField(verbose_name='Địa chỉ chi tiết', blank=True, default='')

    # Tỉnh/Thành phố
    province = models.CharField(max_length=100, verbose_name='Tỉnh/Thành phố', blank=True, default='')
    province_code = models.CharField(max_length=10, verbose_name='Mã tỉnh/thành phố', blank=True, default='')

    # Quận/Huyện
    district = models.CharField(max_length=100, verbose_name='Quận/Huyện', blank=True, default='')
    district_code = models.CharField(max_length=10, verbose_name='Mã quận/huyện', blank=True, default='')

    # Phường/Xã
    ward = models.CharField(max_length=100, blank=True, verbose_name='Phường/Xã')
    ward_code = models.CharField(max_length=10, blank=True, verbose_name='Mã phường/xã')

    is_default = models.BooleanField(default=False, verbose_name='Địa chỉ mặc định')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')

    class Meta:
        verbose_name = 'Địa chỉ'
        verbose_name_plural = 'Địa chỉ'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.address}, {self.district}, {self.province}"

    def get_full_address(self):
        """Lấy địa chỉ đầy đủ"""
        parts = [self.address]
        if self.ward:
            parts.append(self.ward)
        parts.extend([self.district, self.province])
        return ', '.join(filter(None, parts))

    def save(self, *args, **kwargs):
        """Override save để đảm bảo chỉ có 1 địa chỉ mặc định"""
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class SavedCard(models.Model):
    """Model lưu thẻ thanh toán"""

    CARD_TYPES = [
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
        ('jcb', 'JCB'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='saved_cards',
        verbose_name='Người dùng'
    )
    card_type = models.CharField(
        max_length=20,
        choices=CARD_TYPES,
        verbose_name='Loại thẻ'
    )
    masked_number = models.CharField(
        max_length=19,
        verbose_name='Số thẻ đã che'
    )  # ****-****-****-1234
    last_four = models.CharField(
        max_length=4,
        verbose_name='4 số cuối'
    )
    cardholder_name = models.CharField(
        max_length=100,
        verbose_name='Tên chủ thẻ'
    )
    expiry_month = models.PositiveSmallIntegerField(verbose_name='Tháng hết hạn')
    expiry_year = models.PositiveSmallIntegerField(verbose_name='Năm hết hạn')
    is_default = models.BooleanField(default=False, verbose_name='Thẻ mặc định')
    is_expired = models.BooleanField(default=False, verbose_name='Đã hết hạn')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')

    class Meta:
        verbose_name = 'Thẻ đã lưu'
        verbose_name_plural = 'Thẻ đã lưu'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.get_card_type_display()} {self.masked_number}"

    def get_expiry_display(self):
        """Hiển thị ngày hết hạn"""
        return f"{self.expiry_month:02d}/{self.expiry_year}"

    def save(self, *args, **kwargs):
        """Override save để đảm bảo chỉ có 1 thẻ mặc định"""
        if self.is_default:
            SavedCard.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class SocialAccount(models.Model):
    """Model lưu thông tin đăng nhập social (Google, Facebook)"""

    PROVIDER_CHOICES = [
        ('google', 'Google'),
        ('facebook', 'Facebook'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='social_accounts',
        verbose_name='Người dùng'
    )
    provider = models.CharField(
        max_length=20,
        choices=PROVIDER_CHOICES,
        verbose_name='Nhà cung cấp'
    )
    provider_email = models.EmailField(verbose_name='Email từ nhà cung cấp')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')

    class Meta:
        verbose_name = 'Tài khoản Social'
        verbose_name_plural = 'Tài khoản Social'
        unique_together = ['user', 'provider']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.get_provider_display()}"


class UserSession(models.Model):
    """Model quản lý phiên đăng nhập của người dùng"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_sessions',
        verbose_name='Người dùng'
    )
    session_key = models.CharField(max_length=40, verbose_name='Session Key')
    device = models.CharField(max_length=200, blank=True, verbose_name='Thiết bị')
    browser = models.CharField(max_length=100, blank=True, verbose_name='Trình duyệt')
    os = models.CharField(max_length=100, blank=True, verbose_name='Hệ điều hành')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='Địa chỉ IP')
    location = models.CharField(max_length=200, blank=True, verbose_name='Vị trí')
    is_current = models.BooleanField(default=False, verbose_name='Phiên hiện tại')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Đăng nhập lúc')
    last_activity = models.DateTimeField(auto_now=True, verbose_name='Hoạt động cuối')

    class Meta:
        verbose_name = 'Phiên đăng nhập'
        verbose_name_plural = 'Phiên đăng nhập'
        ordering = ['-last_activity']

    def __str__(self):
        return f"{self.user.username} - {self.device or 'Unknown'} - {self.ip_address}"


class LoginHistory(models.Model):
    """Model lưu lịch sử đăng nhập"""

    STATUS_CHOICES = [
        ('success', 'Thành công'),
        ('failed', 'Thất bại'),
        ('2fa_required', 'Yêu cầu 2FA'),
    ]

    PROVIDER_CHOICES = [
        ('email', 'Email/Password'),
        ('google', 'Google'),
        ('facebook', 'Facebook'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='login_history',
        verbose_name='Người dùng'
    )
    login_time = models.DateTimeField(auto_now_add=True, verbose_name='Thời gian đăng nhập')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='Địa chỉ IP')
    device = models.CharField(max_length=200, blank=True, verbose_name='Thiết bị')
    browser = models.CharField(max_length=100, blank=True, verbose_name='Trình duyệt')
    os = models.CharField(max_length=100, blank=True, verbose_name='Hệ điều hành')
    location = models.CharField(max_length=200, blank=True, verbose_name='Vị trí')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='success',
        verbose_name='Trạng thái'
    )
    provider = models.CharField(
        max_length=20,
        choices=PROVIDER_CHOICES,
        default='email',
        verbose_name='Phương thức'
    )
    user_agent = models.TextField(blank=True, verbose_name='User Agent')

    class Meta:
        verbose_name = 'Lịch sử đăng nhập'
        verbose_name_plural = 'Lịch sử đăng nhập'
        ordering = ['-login_time']

    def __str__(self):
        return f"{self.user.username} - {self.login_time} - {self.status}"
