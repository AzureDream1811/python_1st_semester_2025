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

    email = models.EmailField(unique=True, verbose_name='Email')
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
    # Thông tin bổ sung
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

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name='Người dùng'
    )
    full_name = models.CharField(max_length=100, verbose_name='Họ tên người nhận')
    address = models.TextField(blank=True, verbose_name='Địa chỉ')
    city = models.CharField(max_length=100, blank=True, verbose_name='Thành phố')
    city_code = models.CharField(max_length=10, blank=True, verbose_name='Mã thành phố')
    district = models.CharField(max_length=100, blank=True, verbose_name='Quận/Huyện')
    district_code = models.CharField(max_length=10, blank=True, verbose_name='Mã quận/huyện')
    ward = models.CharField(max_length=100, blank=True, verbose_name='Phường/Xã')
    ward_code = models.CharField(max_length=10, blank=True, verbose_name='Mã phường/xã')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Địa chỉ'
        verbose_name_plural = 'Địa chỉ'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.address}, {self.district}, {self.city}"

    def get_full_address(self):
        """Lấy địa chỉ đầy đủ"""
        parts = [self.address]
        if self.ward:
            parts.append(self.ward)
        parts.extend([self.district, self.city])
        return ', '.join(parts)
