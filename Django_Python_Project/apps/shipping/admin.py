"""
Admin Configuration cho Shipping App - ElectroShop

Quản lý các models vận chuyển:
- CarrierConfig: Cấu hình đơn vị vận chuyển (GHN, GHTK, VNPost...)
- Shipment: Đơn vận chuyển
- ShipmentTracking: Theo dõi trạng thái vận chuyển
- ShippingRate: Bảng giá vận chuyển
"""
from django.contrib import admin
from django.utils.html import format_html
from apps.shipping.models import CarrierConfig, Shipment, ShipmentTracking, ShippingRate


@admin.register(CarrierConfig)
class CarrierConfigAdmin(admin.ModelAdmin):
    """
    Quản lý cấu hình đơn vị vận chuyển trong Admin
    
    Cấu hình API key, webhook cho các đơn vị: GHN, GHTK, VNPost, J&T...
    """
    # Các cột hiển thị
    list_display = ['carrier', 'name', 'is_active', 'is_default']

    # Bộ lọc
    list_filter = ['is_active', 'is_default', 'carrier']

    # Các trường có thể tìm kiếm
    search_fields = ['name', 'carrier']

    # Cho phép sửa trực tiếp
    list_editable = ['is_active', 'is_default']

    # Số bản ghi mỗi trang
    list_per_page = 25


class ShipmentTrackingInline(admin.TabularInline):
    """
    Inline hiển thị lịch sử tracking trong trang chi tiết Shipment
    Cho phép xem timeline vận chuyển
    """
    model = ShipmentTracking
    extra = 0  # Không tạo form trống
    readonly_fields = ['status', 'location', 'description', 'timestamp']
    can_delete = False  # Không cho phép xóa tracking


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    """
    Quản lý đơn vận chuyển trong Admin
    
    Theo dõi trạng thái giao hàng của các đơn hàng
    """
    # Các cột hiển thị
    list_display = ['tracking_code', 'order', 'carrier', 'status_display', 'shipping_fee_display', 'estimated_delivery',
                    'created_at']

    # Bộ lọc
    list_filter = ['carrier', 'status', 'created_at']

    # Các trường có thể tìm kiếm
    search_fields = ['tracking_code', 'order__order_number']

    # Inline tracking
    inlines = [ShipmentTrackingInline]

    # Sử dụng raw_id để chọn order nhanh
    raw_id_fields = ['order']

    # Số bản ghi mỗi trang
    list_per_page = 25

    # Phân cấp theo ngày
    date_hierarchy = 'created_at'

    def status_display(self, obj):
        """Hiển thị trạng thái với màu sắc"""
        colors = {
            'pending': 'orange',
            'picked_up': 'blue',
            'in_transit': 'purple',
            'out_for_delivery': 'cyan',
            'delivered': 'green',
            'failed': 'red',
            'returned': 'gray',
        }
        color = colors.get(obj.status, 'black')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.get_status_display())

    status_display.short_description = 'Trạng thái'

    def shipping_fee_display(self, obj):
        """Hiển thị phí ship với format VND"""
        return f"{obj.shipping_fee:,.0f}đ"

    shipping_fee_display.short_description = 'Phí ship'


@admin.register(ShippingRate)
class ShippingRateAdmin(admin.ModelAdmin):
    """
    Quản lý bảng giá vận chuyển trong Admin
    
    Cấu hình giá ship theo tuyến đường và trọng lượng
    """
    # Các cột hiển thị
    list_display = ['carrier', 'from_province', 'to_province', 'weight_range_display', 'price_display']

    # Bộ lọc
    list_filter = ['carrier', 'from_province', 'to_province']

    # Các trường có thể tìm kiếm
    search_fields = ['from_province', 'to_province']

    # Số bản ghi mỗi trang
    list_per_page = 50

    def weight_range_display(self, obj):
        """Hiển thị khoảng trọng lượng"""
        return f"{obj.weight_from}kg - {obj.weight_to}kg"

    weight_range_display.short_description = 'Trọng lượng'

    def price_display(self, obj):
        """Hiển thị giá với format VND"""
        return f"{obj.price:,.0f}đ"

    price_display.short_description = 'Giá'
