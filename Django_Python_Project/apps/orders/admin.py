from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, OrderHistory

class OrderItemInline(admin.TabularInline):
    """
    Inline để hiển thị danh sách sản phẩm trong đơn hàng
    Cho phép xem các items ngay trong trang chi tiết Order mà không cần mở trang riêng
    """
    model = OrderItem
    extra = 0  # Không tạo form trống để thêm item mới
    readonly_fields = ['product', 'product_name', 'product_image', 'price', 'quantity', 'get_total_price']
    can_delete = False  # Không cho phép xóa items

    def get_total_price(self, obj):
        """
        Hiển thị thành tiền cho từng item
        Vì total_price là @property nên phải dùng method để hiển thị trong admin
        """
        if obj.id:
            return f"{obj.total_price:,.0f}đ"
        return "0đ"

    get_total_price.short_description = 'Thành tiền'


class OrderHistoryInline(admin.TabularInline):
    """
    Inline để hiển thị lịch sử thay đổi trạng thái đơn hàng
    Giúp admin theo dõi được các thay đổi của đơn hàng theo thời gian
    """
    model = OrderHistory
    extra = 0
    readonly_fields = ['status', 'created_at']  # Chỉ xem, không chỉnh sửa
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Admin class chính để quản lý đơn hàng
    Cung cấp giao diện đầy đủ để xem, tìm kiếm, lọc và cập nhật đơn hàng
    """
    list_display = [
        'order_number',
        'full_name',
        'phone',
        'total_display',
        'payment_method_display',
        'payment_status_display',
        'status_display',
        'created_at'
    ]

    list_filter = ['status', 'payment_status', 'payment_method', 'created_at', 'city']

    search_fields = ['order_number', 'full_name', 'email', 'phone']

    readonly_fields = ['order_number', 'subtotal', 'total', 'created_at', 'updated_at']

    inlines = [OrderItemInline, OrderHistoryInline]

    date_hierarchy = 'created_at'

    fieldsets = (
        ('Thông tin đơn hàng', {
            'fields': ('order_number', 'user', 'status')
        }),
        ('Thông tin giao hàng', {
            'fields': ('full_name', 'email', 'phone', 'address', 'ward', 'district', 'city', 'note')
        }),
        ('Thanh toán', {
            'fields': ('payment_method', 'payment_status', 'subtotal', 'shipping_fee', 'discount', 'total')
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def total_display(self, obj):
        """Hiển thị tổng tiền với format tiền tệ VN"""
        return f"{obj.total:,.0f}đ"

    total_display.short_description = 'Tổng tiền'

    def payment_method_display(self, obj):
        """Hiển thị tên phương thức thanh toán (tiếng Việt)"""
        return obj.get_payment_method_display()

    payment_method_display.short_description = 'Phương thức'

    def payment_status_display(self, obj):
        """
        Hiển thị trạng thái thanh toán với màu sắc
        - pending: cam (chờ thanh toán)
        - paid: xanh lá (đã thanh toán)
        - failed: đỏ (thất bại)
        - refunded: xám (đã hoàn tiền)
        """
        colors = {
            'pending': 'orange',
            'paid': 'green',
            'failed': 'red',
            'refunded': 'gray',
        }
        color = colors.get(obj.payment_status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_payment_status_display()
        )

    payment_status_display.short_description = 'TT thanh toán'

    def status_display(self, obj):
        """
        Hiển thị trạng thái đơn hàng với màu sắc tương ứng
        Giúp admin dễ dàng phân biệt trạng thái đơn hàng
        """
        colors = {
            'pending': 'orange',  # Chờ xác nhận
            'confirmed': 'blue',  # Đã xác nhận
            'processing': 'purple',  # Đang xử lý
            'shipping': 'cyan',  # Đang giao hàng
            'delivered': 'green',  # Đã giao hàng
            'completed': 'green',  # Hoàn thành
            'cancelled': 'red',  # Đã hủy
            'refunded': 'gray',  # Đã hoàn tiền
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )

    status_display.short_description = 'Trạng thái'

    def save_model(self, request, obj, form, change):
        """
        Override method save_model để tự động tạo lịch sử
        Mỗi khi admin thay đổi trạng thái đơn hàng, hệ thống sẽ tự động
        ghi lại vào bảng OrderHistory để theo dõi
        """
        super().save_model(request, obj, form, change)

        # Kiểm tra nếu đang cập nhật (không phải tạo mới) và có thay đổi status
        if change and 'status' in form.changed_data:
            OrderHistory.objects.create(
                order=obj,
                status=obj.status
            )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Admin để quản lý riêng từng OrderItem
    Hữu ích khi cần xem tất cả items độc lập, không qua Order
    """
    list_display = ['order', 'product_name', 'price_display', 'quantity', 'total_price_display']
    list_filter = ['order__status']
    search_fields = ['product_name', 'order__order_number']
    raw_id_fields = ['order', 'product']  # Dùng popup thay vì dropdown cho ForeignKey

    def price_display(self, obj):
        """Format đơn giá"""
        return f"{obj.price:,.0f}đ"

    price_display.short_description = 'Đơn giá'

    def total_price_display(self, obj):
        """Format thành tiền"""
        return f"{obj.total_price:,.0f}đ"

    total_price_display.short_description = 'Thành tiền'


@admin.register(OrderHistory)
class OrderHistoryAdmin(admin.ModelAdmin):
    """
    Admin để xem lịch sử thay đổi của tất cả đơn hàng
    Giúp theo dõi timeline các thay đổi trạng thái
    """
    list_display = ['order', 'status_display', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order__order_number']
    raw_id_fields = ['order']  # Dùng popup để chọn Order

    def status_display(self, obj):
        """Hiển thị tên trạng thái tiếng Việt từ STATUS_CHOICES của Order"""
        status_dict = dict(Order.STATUS_CHOICES)
        return status_dict.get(obj.status, obj.status)

    status_display.short_description = 'Trạng thái'
