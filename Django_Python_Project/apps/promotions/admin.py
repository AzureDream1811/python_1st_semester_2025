"""
Admin Configuration cho Promotions App - ElectroShop
"""
from django.contrib import admin
from django.utils.html import format_html
from apps.promotions.models import Voucher, VoucherUsage, ComboDeal, FlashSale


@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    """
    Quản lý mã giảm giá trong Admin
    Hỗ trợ tạo voucher với giảm giá theo % hoặc số tiền cố định
    """
    # Các cột hiển thị
    list_display = ['code', 'name', 'discount_type', 'discount_value_display', 'usage_display', 'is_active',
                    'valid_until']

    # Bộ lọc
    list_filter = ['discount_type', 'is_active', 'valid_from', 'valid_until']

    # Các trường có thể tìm kiếm
    search_fields = ['code', 'name']

    # Cho phép sửa trực tiếp
    list_editable = ['is_active']

    # Số bản ghi mỗi trang
    list_per_page = 25

    def discount_value_display(self, obj):
        """Hiển thị giá trị giảm giá với format phù hợp"""
        if obj.discount_type == 'percent':
            return f"{obj.discount_value}%"
        return f"{obj.discount_value:,.0f}đ"

    discount_value_display.short_description = 'Giảm giá'

    def usage_display(self, obj):
        """Hiển thị số lần sử dụng / giới hạn"""
        if obj.usage_limit:
            return f"{obj.used_count}/{obj.usage_limit}"
        return f"{obj.used_count}/∞"

    usage_display.short_description = 'Đã dùng'


@admin.register(VoucherUsage)
class VoucherUsageAdmin(admin.ModelAdmin):
    """
    Quản lý lịch sử sử dụng voucher trong Admin
    Theo dõi ai đã sử dụng voucher nào, cho đơn hàng nào
    """
    # Các cột hiển thị
    list_display = ['voucher', 'user', 'order', 'discount_amount_display', 'used_at']

    # Bộ lọc theo thời gian
    list_filter = ['used_at', 'voucher']

    # Các trường có thể tìm kiếm
    search_fields = ['voucher__code', 'user__username', 'user__email', 'order__order_number']

    # Sử dụng raw_id để chọn nhanh
    raw_id_fields = ['voucher', 'user', 'order']

    # Số bản ghi mỗi trang
    list_per_page = 25

    def discount_amount_display(self, obj):
        """Hiển thị số tiền giảm với format VND"""
        return f"{obj.discount_amount:,.0f}đ"

    discount_amount_display.short_description = 'Số tiền giảm'


@admin.register(ComboDeal)
class ComboDealAdmin(admin.ModelAdmin):
    """
    Quản lý combo khuyến mãi trong Admin
    Tạo combo nhiều sản phẩm với giá ưu đãi
    """
    # Các cột hiển thị
    list_display = ['name', 'discount_type', 'discount_value_display', 'product_count', 'is_active', 'valid_until']

    # Bộ lọc
    list_filter = ['is_active', 'discount_type', 'valid_from', 'valid_until']

    # Các trường có thể tìm kiếm
    search_fields = ['name']

    # Widget chọn nhiều sản phẩm
    filter_horizontal = ['products']

    # Cho phép sửa trực tiếp
    list_editable = ['is_active']

    # Số bản ghi mỗi trang
    list_per_page = 25

    def discount_value_display(self, obj):
        """Hiển thị giá trị giảm giá với format phù hợp"""
        if obj.discount_type == 'percent':
            return f"{obj.discount_value}%"
        return f"{obj.discount_value:,.0f}đ"

    discount_value_display.short_description = 'Giảm giá'

    def product_count(self, obj):
        """Đếm số sản phẩm trong combo"""
        return obj.products.count()

    product_count.short_description = 'Số SP'


@admin.register(FlashSale)
class FlashSaleAdmin(admin.ModelAdmin):
    """
    Quản lý Flash Sale trong Admin
    Tạo chương trình giảm giá theo thời gian cho từng sản phẩm
    """
    # Các cột hiển thị
    list_display = ['product', 'sale_price_display', 'sold_display', 'start_time', 'end_time', 'is_active',
                    'status_display']

    # Bộ lọc
    list_filter = ['is_active', 'start_time', 'end_time']

    # Các trường có thể tìm kiếm
    search_fields = ['product__name']

    # Sử dụng raw_id để chọn sản phẩm nhanh
    raw_id_fields = ['product']

    # Cho phép sửa trực tiếp
    list_editable = ['is_active']

    # Số bản ghi mỗi trang
    list_per_page = 25

    def sale_price_display(self, obj):
        """Hiển thị giá sale với format VND"""
        return f"{obj.sale_price:,.0f}đ"

    sale_price_display.short_description = 'Giá Flash Sale'

    def sold_display(self, obj):
        """Hiển thị số lượng đã bán / giới hạn"""
        if obj.quantity_limit:
            return f"{obj.sold_count}/{obj.quantity_limit}"
        return f"{obj.sold_count}/∞"

    sold_display.short_description = 'Đã bán'

    def status_display(self, obj):
        """Hiển thị trạng thái Flash Sale với màu sắc"""
        from django.utils import timezone
        now = timezone.now()

        if not obj.is_active:
            return format_html('<span style="color: gray;">Tắt</span>')
        elif obj.start_time > now:
            return format_html('<span style="color: orange;">⏳ Chờ bắt đầu</span>')
        elif obj.end_time < now:
            return format_html('<span style="color: gray;">Đã kết thúc</span>')
        else:
            return format_html('<span style="color: green; font-weight: bold;">🔥 Đang diễn ra</span>')

    status_display.short_description = 'Trạng thái'
