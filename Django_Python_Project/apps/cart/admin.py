from django.contrib import admin
from django.utils.html import format_html
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    """Inline hiển thị sản phẩm trong giỏ hàng"""
    model = CartItem
    extra = 0
    raw_id_fields = ['product']
    readonly_fields = ['price_display', 'total_price_display']

    def price_display(self, obj):
        """Hiển thị đơn giá"""
        if obj.pk:
            return f"{obj.price:,.0f}đ"
        return "-"

    price_display.short_description = 'Đơn giá'

    def total_price_display(self, obj):
        """Hiển thị thành tiền"""
        if obj.pk:
            return f"{obj.total_price:,.0f}đ"
        return "-"

    total_price_display.short_description = 'Thành tiền'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Quản lý giỏ hàng"""
    list_display = ['id', 'user_display', 'session_key_display', 'total_items', 'subtotal_display', 'created_at',
                    'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__email', 'user__username', 'session_key']
    inlines = [CartItemInline]
    raw_id_fields = ['user']
    readonly_fields = ['total_items', 'subtotal_display', 'created_at', 'updated_at']
    list_per_page = 25
    date_hierarchy = 'created_at'

    def user_display(self, obj):
        """Hiển thị user với link"""
        if obj.user:
            return format_html('<a href="/admin/auth/user/{}/change/">{}</a>', obj.user.pk, obj.user.username)
        return format_html('<span style="color: gray;">Khách vãng lai</span>')

    user_display.short_description = 'Người dùng'

    def session_key_display(self, obj):
        """Hiển thị session key rút gọn"""
        if obj.session_key:
            return f"...{obj.session_key[-8:]}"
        return "-"

    session_key_display.short_description = 'Session'

    def subtotal_display(self, obj):
        """Hiển thị tổng tiền với format"""
        return format_html('<strong style="color: green;">{:,.0f}đ</strong>', obj.subtotal)

    subtotal_display.short_description = 'Tổng tiền'

    actions = ['clear_old_carts']

    def clear_old_carts(self, request, queryset):
        """Xóa các giỏ hàng đã chọn"""
        count = queryset.count()
        for cart in queryset:
            cart.clear()
        queryset.delete()
        self.message_user(request, f'Đã xóa {count} giỏ hàng')

    clear_old_carts.short_description = 'Xóa giỏ hàng đã chọn'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Quản lý sản phẩm trong giỏ hàng"""
    list_display = ['cart', 'product', 'quantity', 'price_display', 'total_price_display', 'created_at']
    list_filter = ['created_at', 'cart__user']
    search_fields = ['product__name', 'cart__user__email', 'cart__user__username']
    raw_id_fields = ['cart', 'product']
    list_per_page = 25

    def price_display(self, obj):
        """Hiển thị đơn giá"""
        return f"{obj.price:,.0f}đ"

    price_display.short_description = 'Đơn giá'

    def total_price_display(self, obj):
        """Hiển thị thành tiền"""
        return format_html('<strong>{:,.0f}đ</strong>', obj.total_price)

    total_price_display.short_description = 'Thành tiền'
