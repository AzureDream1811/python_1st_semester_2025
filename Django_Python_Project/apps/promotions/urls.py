"""
URL Configuration cho Promotions App - ElectroShop
==================================================

Định nghĩa các URL patterns cho module khuyến mãi:
- Flash Sale: Danh sách và chi tiết
- Combo Deal: Danh sách combo
- Voucher: Xác thực và áp dụng mã giảm giá

Tác giả: ElectroShop Team
"""
from django.urls import path
from . import views

# Namespace cho app promotions
# Sử dụng: {% url 'promotions:flash_sales' %}
app_name = 'promotions'

urlpatterns = [
    # =========================================================================
    # FLASH SALE URLs
    # =========================================================================

    # Danh sách flash sale đang diễn ra
    # URL: /promotions/flash-sales/
    path('flash-sales/', views.flash_sale_list, name='flash_sales'),

    # Chi tiết một flash sale
    # URL: /promotions/flash-sales/1/
    path('flash-sales/<int:pk>/', views.flash_sale_detail, name='flash_sale_detail'),

    # =========================================================================
    # COMBO DEAL URLs
    # =========================================================================

    # Danh sách combo khuyến mãi
    # URL: /promotions/combo-deals/
    path('combo-deals/', views.combo_deal_list, name='combo_deals'),

    # =========================================================================
    # VOUCHER URLs
    # =========================================================================

    # Danh sách voucher của user (yêu cầu đăng nhập)
    # URL: /promotions/my-vouchers/
    path('my-vouchers/', views.my_vouchers, name='my_vouchers'),

    # API: Xác thực mã voucher (POST)
    # URL: /promotions/validate-voucher/
    path('validate-voucher/', views.validate_voucher, name='validate_voucher'),

    # API: Áp dụng voucher vào giỏ hàng (POST)
    # URL: /promotions/apply-voucher/
    path('apply-voucher/', views.apply_voucher, name='apply_voucher'),
]
