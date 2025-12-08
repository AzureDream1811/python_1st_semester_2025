from django.contrib import admin
from .models import Profile, Address

@admin.register(Profile)
@admin.register(Address)
class ProfileAdmin(admin.ModelAdmin):
    """Quản lý Profile trong Admin"""
    list_display = ['user', 'phone', 'email', 'gender', 'date_of_birth', 'created_at']
    list_filter = ['gender', 'created_at', 'updated_at']
    search_fields = ['user__username', 'user__email', 'phone', 'email', 'user__first_name']
    readonly_fields = ['created_at', 'updated_at']

    # Nhóm các trường để hiển thị gọn gàng hơn
    fieldsets = (
        ('Thông tin tài khoản', {
            'fields': ('user', 'email', 'avatar')
        }),
        ('Thông tin cá nhân', {
            'fields': ('phone', 'gender', 'date_of_birth', 'address')
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Cho phép ẩn/hiện nhóm này
        }),
    )