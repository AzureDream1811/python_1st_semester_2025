from django.contrib import admin
from django.utils.html import format_html
from .models import Profile, Address


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Quản lý Profile trong Admin"""
    list_display = ['user', 'phone', 'email', 'gender', 'avatar_preview', 'date_of_birth', 'created_at']
    list_filter = ['gender', 'created_at', 'updated_at']
    search_fields = ['user__username', 'user__email', 'phone', 'email', 'user__first_name']
    readonly_fields = ['created_at', 'updated_at', 'avatar_preview']
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
        """Hiển thị avatar preview"""
        if obj.avatar:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.avatar.url)
        return format_html('<span style="color: gray;">Chưa có avatar</span>')
    avatar_preview.short_description = 'Avatar'


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Quản lý địa chỉ giao hàng"""
    list_display = ['full_name', 'user', 'city', 'district', 'ward', 'address', 'created_at']
    list_filter = ['city', 'district', 'created_at']
    search_fields = ['full_name', 'user__username', 'user__email', 'address', 'city', 'district', 'ward']
    raw_id_fields = ['user']
    list_per_page = 25

    fieldsets = (
        ('Người dùng', {
            'fields': ('user',)
        }),
        ('Thông tin người nhận', {
            'fields': ('full_name',)
        }),
        ('Địa chỉ', {
            'fields': ('address', 'ward', 'ward_code', 'district', 'district_code', 'city', 'city_code')
        }),
    )
