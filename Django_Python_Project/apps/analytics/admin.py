"""
Admin Configuration cho Analytics App

"""
from django.contrib import admin
from apps.analytics.models import FunnelEvent, SearchLog, DailyStats


@admin.register(FunnelEvent)
class FunnelEventAdmin(admin.ModelAdmin):
    """
    Quản lý sự kiện Funnel trong Admin
    
    Theo dõi hành trình người dùng: Xem SP -> Thêm giỏ -> Thanh toán -> Hoàn thành
    """
    # Các cột hiển thị
    list_display = ['session_id', 'step', 'user', 'product', 'created_at']

    # Bộ lọc theo bước funnel và thời gian
    list_filter = ['step', 'created_at']

    # Các trường có thể tìm kiếm
    search_fields = ['session_id', 'user__username', 'user__email', 'product__name']

    # Sử dụng raw_id để chọn nhanh
    raw_id_fields = ['user', 'product']

    # Số bản ghi mỗi trang
    list_per_page = 50

    # Sắp xếp theo thời gian mới nhất
    ordering = ['-created_at']


@admin.register(SearchLog)
class SearchLogAdmin(admin.ModelAdmin):
    """
    Quản lý lịch sử tìm kiếm trong Admin
    
    Phân tích từ khóa tìm kiếm phổ biến và từ khóa không có kết quả
    """
    # Các cột hiển thị
    list_display = ['query', 'results_count', 'user', 'clicked_product', 'created_at']

    # Bộ lọc theo thời gian và số kết quả
    list_filter = ['created_at', 'results_count']

    # Các trường có thể tìm kiếm
    search_fields = ['query', 'user__username', 'user__email']

    # Sử dụng raw_id để chọn nhanh
    raw_id_fields = ['user', 'clicked_product']

    # Số bản ghi mỗi trang
    list_per_page = 50

    # Sắp xếp theo thời gian mới nhất
    ordering = ['-created_at']


@admin.register(DailyStats)
class DailyStatsAdmin(admin.ModelAdmin):
    """
    Quản lý thống kê ngày trong Admin
    
    Xem tổng quan doanh thu, đơn hàng, lượt truy cập theo ngày
    """
    # Các cột hiển thị
    list_display = ['date', 'total_revenue', 'total_orders', 'total_visitors', 'conversion_rate', 'avg_order_value']

    # Bộ lọc theo ngày
    list_filter = ['date']

    # Số bản ghi mỗi trang
    list_per_page = 31  # Hiển thị 1 tháng

    # Sắp xếp theo ngày mới nhất
    ordering = ['-date']

    # Các trường chỉ đọc
    readonly_fields = ['created_at', 'updated_at']

    # Phân cấp theo ngày
    date_hierarchy = 'date'
