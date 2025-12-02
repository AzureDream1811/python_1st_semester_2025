from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class User(AbstractUser):
    """Custom User Model với thông tin bổ sung"""

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

    # Thông tin bổ sung
    is_verified = models.BooleanField(default=False, verbose_name='Đã xác thực')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')

    class Meta:
        verbose_name = 'Người dùng'
        verbose_name_plural = 'Người dùng'
        ordering = ['-created_at']

    def __str__(self):
        return self.email or self.username

    def get_full_name(self):
        """Lấy họ tên đầy đủ"""
        if self.first_name and self.last_name:
            return f"{self.last_name} {self.first_name}"
        return self.username

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
    phone = models.CharField(max_length=15, verbose_name='Số điện thoại')
    address_line = models.CharField(max_length=255, verbose_name='Địa chỉ')
    ward = models.CharField(max_length=100, blank=True, verbose_name='Phường/Xã')
    district = models.CharField(max_length=100, verbose_name='Quận/Huyện')
    city = models.CharField(max_length=100, verbose_name='Tỉnh/Thành phố')
    is_default = models.BooleanField(default=False, verbose_name='Địa chỉ mặc định')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Địa chỉ'
        verbose_name_plural = 'Địa chỉ'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.address_line}, {self.district}, {self.city}"

    def get_full_address(self):
        """Lấy địa chỉ đầy đủ"""
        parts = [self.address_line]
        if self.ward:
            parts.append(self.ward)
        parts.extend([self.district, self.city])
        return ', '.join(parts)

    def save(self, *args, **kwargs):
        # Nếu đặt làm địa chỉ mặc định, bỏ mặc định các địa chỉ khác
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
