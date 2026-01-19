"""
Admin Configuration cho Notifications App - ElectroShop
"""
from django.contrib import admin
from django.utils.html import format_html
from apps.notifications.models import Notification, PushSubscription, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Quản lý thông báo trong Admin
    
    Xem và quản lý tất cả thông báo gửi đến người dùng
    """
    # Các cột hiển thị
    list_display = ['user', 'notification_type_display', 'title', 'is_read_display', 'created_at']

    # Bộ lọc
    list_filter = ['notification_type', 'is_read', 'created_at']

    # Các trường có thể tìm kiếm
    search_fields = ['user__username', 'user__email', 'title', 'message']

    # Các trường chỉ đọc
    readonly_fields = ['created_at', 'read_at']

    # Sắp xếp theo thời gian mới nhất
    ordering = ['-created_at']

    # Sử dụng raw_id để chọn user nhanh
    raw_id_fields = ['user']

    # Số bản ghi mỗi trang
    list_per_page = 50

    def notification_type_display(self, obj):
        """Hiển thị loại thông báo với icon"""
        icons = {
            'order': '📦',
            'promotion': '🎁',
            'system': '⚙️',
            'chat': '💬',
        }
        icon = icons.get(obj.notification_type, '📢')
        return format_html('{} {}', icon, obj.get_notification_type_display())

    notification_type_display.short_description = 'Loại'

    def is_read_display(self, obj):
        """Hiển thị trạng thái đã đọc với icon"""
        if obj.is_read:
            return format_html('<span style="color: green;">✓ Đã đọc</span>')
        return format_html('<span style="color: orange;">○ Chưa đọc</span>')

    is_read_display.short_description = 'Trạng thái'


@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    """
    Quản lý đăng ký push notification trong Admin
    
    Theo dõi các thiết bị đã đăng ký nhận push notification
    """
    # Các cột hiển thị
    list_display = ['user', 'is_active_display', 'device_info', 'created_at', 'last_used']

    # Bộ lọc
    list_filter = ['is_active', 'created_at']

    # Các trường có thể tìm kiếm
    search_fields = ['user__username', 'user__email']

    # Sử dụng raw_id để chọn user nhanh
    raw_id_fields = ['user']

    # Số bản ghi mỗi trang
    list_per_page = 50

    def is_active_display(self, obj):
        """Hiển thị trạng thái hoạt động với icon"""
        if obj.is_active:
            return format_html('<span style="color: green;">✓ Hoạt động</span>')
        return format_html('<span style="color: gray;">✗ Tắt</span>')

    is_active_display.short_description = 'Trạng thái'

    def device_info(self, obj):
        """Hiển thị thông tin thiết bị (nếu có)"""
        # Có thể mở rộng để hiển thị thông tin thiết bị từ subscription data
        return '-'

    device_info.short_description = 'Thiết bị'


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    """
    Quản lý cài đặt thông báo trong Admin
    
    Xem và chỉnh sửa cài đặt thông báo của từng người dùng
    """
    # Các cột hiển thị
    list_display = ['user', 'email_order_updates', 'push_order_updates', 'push_promotions', 'email_promotions']

    # Các trường có thể tìm kiếm
    search_fields = ['user__username', 'user__email']

    # Sử dụng raw_id để chọn user nhanh
    raw_id_fields = ['user']

    # Cho phép sửa trực tiếp trong danh sách
    list_editable = ['email_order_updates', 'push_order_updates', 'push_promotions']

    # Số bản ghi mỗi trang
    list_per_page = 50
