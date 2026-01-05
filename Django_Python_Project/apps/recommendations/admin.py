"""
Admin Configuration cho Recommendations App - ElectroShop

Quản lý các models gợi ý sản phẩm:
- UserActivity: Hoạt động của người dùng (xem, mua, thêm giỏ...)
- ProductSimilarity: Độ tương đồng giữa các sản phẩm
- FrequentlyBoughtTogether: Sản phẩm thường mua cùng nhau
"""
from django.contrib import admin
from django.utils.html import format_html
from apps.recommendations.models import UserActivity, ProductSimilarity, FrequentlyBoughtTogether


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    """
    Quản lý hoạt động người dùng trong Admin
    
    Theo dõi các hành vi: xem sản phẩm, thêm giỏ hàng, mua hàng...
    Dữ liệu này được sử dụng để tạo gợi ý cá nhân hóa
    """
    # Các cột hiển thị
    list_display = ['user', 'activity_type_display', 'product', 'created_at']

    # Bộ lọc
    list_filter = ['activity_type', 'created_at']

    # Các trường có thể tìm kiếm
    search_fields = ['user__username', 'user__email', 'product__name']

    # Sử dụng raw_id để chọn nhanh
    raw_id_fields = ['user', 'product']

    # Số bản ghi mỗi trang
    list_per_page = 50

    # Phân cấp theo ngày
    date_hierarchy = 'created_at'

    def activity_type_display(self, obj):
        """Hiển thị loại hoạt động với icon"""
        icons = {
            'view': '👁️ Xem',
            'add_to_cart': '🛒 Thêm giỏ',
            'purchase': '💰 Mua',
            'wishlist': '❤️ Yêu thích',
            'review': '⭐ Đánh giá',
        }
        return icons.get(obj.activity_type, obj.activity_type)

    activity_type_display.short_description = 'Hoạt động'


@admin.register(ProductSimilarity)
class ProductSimilarityAdmin(admin.ModelAdmin):
    """
    Quản lý độ tương đồng sản phẩm trong Admin
    
    Dữ liệu được tính toán từ thuật toán ML để gợi ý "Sản phẩm tương tự"
    """
    # Các cột hiển thị
    list_display = ['product', 'similar_product', 'score_display', 'updated_at']

    # Các trường có thể tìm kiếm
    search_fields = ['product__name', 'similar_product__name']

    # Sử dụng raw_id để chọn nhanh
    raw_id_fields = ['product', 'similar_product']

    # Số bản ghi mỗi trang
    list_per_page = 50

    # Sắp xếp theo điểm tương đồng giảm dần
    ordering = ['-score']

    def score_display(self, obj):
        """Hiển thị điểm tương đồng với màu sắc"""
        score = obj.score
        if score >= 0.8:
            color = 'green'
        elif score >= 0.5:
            color = 'orange'
        else:
            color = 'gray'
        return format_html('<span style="color: {}; font-weight: bold;">{:.2f}</span>', color, score)

    score_display.short_description = 'Điểm tương đồng'


@admin.register(FrequentlyBoughtTogether)
class FrequentlyBoughtTogetherAdmin(admin.ModelAdmin):
    """
    Quản lý sản phẩm thường mua cùng trong Admin
    
    Dữ liệu được tính từ lịch sử đơn hàng để gợi ý "Thường mua cùng"
    """
    # Các cột hiển thị
    list_display = ['product', 'related_product', 'count_display', 'updated_at']

    # Các trường có thể tìm kiếm
    search_fields = ['product__name', 'related_product__name']

    # Sử dụng raw_id để chọn nhanh
    raw_id_fields = ['product', 'related_product']

    # Số bản ghi mỗi trang
    list_per_page = 50

    # Sắp xếp theo số lần mua cùng giảm dần
    ordering = ['-count']

    def count_display(self, obj):
        """Hiển thị số lần mua cùng với format"""
        return format_html('<strong>{}</strong> lần', obj.count)

    count_display.short_description = 'Số lần mua cùng'
