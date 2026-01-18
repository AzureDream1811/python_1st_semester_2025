"""
Admin Configuration cho Accounts App - ElectroShop

Quản lý các models:
- Profile: Hồ sơ người dùng mở rộng
- Address: Địa chỉ giao hàng
- SavedCard: Thẻ thanh toán đã lưu
- SocialAccount: Tài khoản đăng nhập social (Google, Facebook)
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Profile, Address, SavedCard, SocialAccount


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Quản lý hồ sơ người dùng trong Admin
    
    Hiển thị thông tin cá nhân, avatar, và các thông tin liên hệ
    """
    # Các cột hiển thị trong danh sách
    list_display = ['user', 'phone', 'email', 'gender', 'avatar_preview', 'date_of_birth', 'created_at']

    # Bộ lọc bên phải
    list_filter = ['gender', 'created_at', 'updated_at']

    # Các trường có thể tìm kiếm
    search_fields = ['user__username', 'user__email', 'phone', 'email', 'user__first_name']

    # Các trường chỉ đọc
    readonly_fields = ['created_at', 'updated_at', 'avatar_preview']

    # Số bản ghi mỗi trang
    list_per_page = 25

    # Nhóm các trường để hiển thị gọn gàng hơn
    fieldsets = (
        ('Thông tin tài khoản', {
            'fields': ('user', 'email', 'avatar', 'avatar_preview')
        }),
        ('Thông tin cá nhân', {
            'fields': ('phone', 'gender', 'date_of_birth', 'address')
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Cho phép ẩn/hiện nhóm này
        }),
    )

    def avatar_preview(self, obj):
        """Hiển thị avatar preview dạng thumbnail"""
        if obj.avatar:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.avatar.url)
        return format_html('<span style="color: gray;">Chưa có avatar</span>')

    avatar_preview.short_description = 'Avatar'


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """
    Quản lý địa chỉ giao hàng trong Admin
    
    Hỗ trợ quản lý địa chỉ theo cấu trúc Tỉnh/Thành phố > Quận/Huyện > Phường/Xã
    """
    # Các cột hiển thị - SỬA LỖI: đổi 'city' thành 'province' theo model
    list_display = ['full_name', 'user', 'province', 'district', 'ward', 'is_default', 'created_at']

    # Bộ lọc - SỬA LỖI: đổi 'city' thành 'province'
    list_filter = ['province', 'district', 'is_default', 'created_at']

    # Các trường có thể tìm kiếm - SỬA LỖI: đổi 'city' thành 'province'
    search_fields = ['full_name', 'user__username', 'user__email', 'address', 'province', 'district', 'ward', 'phone']

    # Sử dụng raw_id để chọn user nhanh hơn
    raw_id_fields = ['user']

    # Số bản ghi mỗi trang
    list_per_page = 25

    # Các trường chỉ đọc
    readonly_fields = ['created_at', 'updated_at']

    # Nhóm các trường - SỬA LỖI: đổi 'city' thành 'province'
    fieldsets = (
        ('Người dùng', {
            'fields': ('user',)
        }),
        ('Thông tin người nhận', {
            'fields': ('full_name', 'phone')
        }),
        ('Địa chỉ chi tiết', {
            'fields': ('address', 'ward', 'ward_code', 'district', 'district_code', 'province', 'province_code')
        }),
        ('Cài đặt', {
            'fields': ('is_default',)
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SavedCard)
class SavedCardAdmin(admin.ModelAdmin):
    """
    Quản lý thẻ thanh toán đã lưu trong Admin
    
    Hiển thị thông tin thẻ đã được mã hóa (masked) để bảo mật
    """
    # Các cột hiển thị
    list_display = ['user', 'card_type', 'masked_number', 'cardholder_name', 'expiry_display', 'is_default',
                    'is_expired', 'created_at']

    # Bộ lọc
    list_filter = ['card_type', 'is_default', 'is_expired', 'created_at']

    # Các trường có thể tìm kiếm
    search_fields = ['user__username', 'user__email', 'cardholder_name', 'last_four']

    # Sử dụng raw_id để chọn user nhanh hơn
    raw_id_fields = ['user']

    # Số bản ghi mỗi trang
    list_per_page = 25

    # Các trường chỉ đọc
    readonly_fields = ['created_at', 'updated_at']

    def expiry_display(self, obj):
        """Hiển thị ngày hết hạn dạng MM/YY"""
        return obj.get_expiry_display()

    expiry_display.short_description = 'Hết hạn'


@admin.register(SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):
    """
    Quản lý tài khoản đăng nhập social trong Admin
    
    Theo dõi các tài khoản Google, Facebook đã liên kết
    """
    # Các cột hiển thị
    list_display = ['user', 'provider', 'provider_email', 'created_at']

    # Bộ lọc theo nhà cung cấp
    list_filter = ['provider', 'created_at']

    # Các trường có thể tìm kiếm
    search_fields = ['user__username', 'user__email', 'provider_email']

    # Sử dụng raw_id để chọn user nhanh hơn
    raw_id_fields = ['user']

    # Số bản ghi mỗi trang
    list_per_page = 25

    # Các trường chỉ đọc
    readonly_fields = ['created_at']
