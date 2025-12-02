from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, OrderHistory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name', 'product_sku', 'price', 'quantity', 'total_price']
    can_delete = False


class OrderHistoryInline(admin.TabularInline):
    model = OrderHistory
    extra = 0
    readonly_fields = ['status', 'note', 'created_by', 'created_at']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'full_name', 'phone', 'total_display',
        'payment_method', 'payment_status', 'status_display', 'created_at'
    ]
    list_filter = ['status', 'payment_status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'full_name', 'email', 'phone']
    readonly_fields = ['order_number', 'subtotal', 'total', 'created_at', 'updated_at']
    inlines = [OrderItemInline, OrderHistoryInline]
    list_editable = ['status']
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
            'fields': ('created_at', 'updated_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_display(self, obj):
        return f"{obj.total:,.0f}đ"
    total_display.short_description = 'Tổng tiền'
    
    def status_display(self, obj):
        colors = {
            'pending': 'orange',
            'confirmed': 'blue',
            'processing': 'purple',
            'shipping': 'cyan',
            'delivered': 'green',
            'completed': 'green',
            'cancelled': 'red',
            'refunded': 'gray',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Trạng thái'
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        # Tạo lịch sử khi admin thay đổi trạng thái
        if change and 'status' in form.changed_data:
            OrderHistory.objects.create(
                order=obj,
                status=obj.status,
                note=f'Admin cập nhật trạng thái thành "{obj.get_status_display()}"',
                created_by=request.user
            )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'price', 'quantity', 'total_price']
    list_filter = ['order__status']
    search_fields = ['product_name', 'order__order_number']
    raw_id_fields = ['order', 'product']


@admin.register(OrderHistory)
class OrderHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'note', 'created_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order__order_number']
    raw_id_fields = ['order', 'created_by']
