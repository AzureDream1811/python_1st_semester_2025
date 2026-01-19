"""
Admin Configuration cho Payments App - ElectroShop

Quản lý các models thanh toán:
- PaymentTransaction: Giao dịch thanh toán
- Refund: Hoàn tiền
- BankAccount: Tài khoản ngân hàng nhận thanh toán
- EWalletAccount: Ví điện tử (MoMo, ZaloPay)
"""
from django.contrib import admin
from django.utils.html import format_html
from apps.payments.models import PaymentTransaction, Refund, BankAccount, EWalletAccount


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    """
    Quản lý giao dịch thanh toán trong Admin
    
    Theo dõi tất cả giao dịch từ các phương thức: COD, VNPay, MoMo, ZaloPay, chuyển khoản
    """
    # Các cột hiển thị
    list_display = ['transaction_id', 'order', 'payment_method', 'amount_display', 'status_display', 'created_at']

    # Bộ lọc theo phương thức và trạng thái
    list_filter = ['payment_method', 'status', 'created_at']

    # Các trường có thể tìm kiếm
    search_fields = ['transaction_id', 'order__order_number']

    # Các trường chỉ đọc (không cho phép sửa)
    readonly_fields = ['transaction_id', 'response_data', 'created_at', 'updated_at']

    # Số bản ghi mỗi trang
    list_per_page = 25

    # Phân cấp theo ngày
    date_hierarchy = 'created_at'

    def amount_display(self, obj):
        """Hiển thị số tiền với format tiền tệ VN"""
        return f"{obj.amount:,.0f}đ"

    amount_display.short_description = 'Số tiền'

    def status_display(self, obj):
        """
        Hiển thị trạng thái với màu sắc
        - pending: cam (chờ xử lý)
        - processing: xanh dương (đang xử lý)
        - success: xanh lá (thành công)
        - failed: đỏ (thất bại)
        - cancelled: xám (đã hủy)
        """
        colors = {
            'pending': 'orange',
            'processing': 'blue',
            'success': 'green',
            'failed': 'red',
            'cancelled': 'gray',
        }
        color = colors.get(obj.status, 'black')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.get_status_display())

    status_display.short_description = 'Trạng thái'


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    """
    Quản lý yêu cầu hoàn tiền trong Admin
    
    Theo dõi các yêu cầu hoàn tiền từ khách hàng
    """
    # Các cột hiển thị
    list_display = ['id', 'payment', 'amount_display', 'reason', 'status_display', 'created_at']

    # Bộ lọc theo trạng thái
    list_filter = ['status', 'created_at']

    # Các trường có thể tìm kiếm
    search_fields = ['payment__transaction_id', 'reason']

    # Số bản ghi mỗi trang
    list_per_page = 25

    def amount_display(self, obj):
        """Hiển thị số tiền hoàn với format tiền tệ VN"""
        return f"{obj.amount:,.0f}đ"

    amount_display.short_description = 'Số tiền hoàn'

    def status_display(self, obj):
        """
        Hiển thị trạng thái hoàn tiền với màu sắc
        - pending: cam (chờ xử lý)
        - processing: xanh dương (đang xử lý)
        - completed: xanh lá (hoàn thành)
        - failed: đỏ (thất bại)
        """
        colors = {
            'pending': 'orange',
            'processing': 'blue',
            'completed': 'green',
            'failed': 'red',
        }
        color = colors.get(obj.status, 'black')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.get_status_display())

    status_display.short_description = 'Trạng thái'


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    """
    Quản lý tài khoản ngân hàng nhận thanh toán trong Admin
    
    Cấu hình các tài khoản ngân hàng để khách hàng chuyển khoản
    """
    # Các cột hiển thị
    list_display = ['bank_name', 'account_number', 'account_name', 'branch', 'is_active', 'is_default', 'created_at']

    # Bộ lọc theo ngân hàng và trạng thái
    list_filter = ['bank_code', 'is_active', 'is_default']

    # Các trường có thể tìm kiếm
    search_fields = ['bank_name', 'account_number', 'account_name']

    # Cho phép sửa trực tiếp trong danh sách
    list_editable = ['is_active', 'is_default']

    # Số bản ghi mỗi trang
    list_per_page = 25

    # Các trường chỉ đọc
    readonly_fields = ['created_at', 'updated_at']

    # Nhóm các trường
    fieldsets = (
        ('Thông tin ngân hàng', {
            'fields': ('bank_code', 'bank_name', 'branch')
        }),
        ('Thông tin tài khoản', {
            'fields': ('account_number', 'account_name')
        }),
        ('Trạng thái', {
            'fields': ('is_active', 'is_default')
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(EWalletAccount)
class EWalletAccountAdmin(admin.ModelAdmin):
    """
    Quản lý ví điện tử nhận thanh toán trong Admin
    
    Cấu hình các ví MoMo, ZaloPay để nhận thanh toán
    """
    # Các cột hiển thị
    list_display = ['wallet_type', 'wallet_id', 'wallet_name', 'is_active', 'is_default', 'created_at']

    # Bộ lọc theo loại ví và trạng thái
    list_filter = ['wallet_type', 'is_active', 'is_default']

    # Các trường có thể tìm kiếm
    search_fields = ['wallet_id', 'wallet_name']

    # Cho phép sửa trực tiếp trong danh sách
    list_editable = ['is_active', 'is_default']

    # Số bản ghi mỗi trang
    list_per_page = 25

    # Các trường chỉ đọc
    readonly_fields = ['created_at', 'updated_at']

    # Nhóm các trường
    fieldsets = (
        ('Thông tin ví', {
            'fields': ('wallet_type', 'wallet_id', 'wallet_name')
        }),
        ('Trạng thái', {
            'fields': ('is_active', 'is_default')
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
