"""
App Configuration cho Promotions - ElectroShop
==============================================

Cấu hình Django app cho module khuyến mãi.

Module này quản lý:
- Voucher/Mã giảm giá
- Combo Deal
- Flash Sale

Tác giả: ElectroShop Team
"""
from django.apps import AppConfig


class PromotionsConfig(AppConfig):
    """
    Cấu hình cho app Promotions
    
    Attributes:
        default_auto_field: Kiểu primary key mặc định
        name: Đường dẫn đầy đủ của app
        verbose_name: Tên hiển thị trong Admin (tiếng Việt)
    """
    # Sử dụng BigAutoField cho primary key (hỗ trợ số lượng lớn)
    default_auto_field = 'django.db.models.BigAutoField'

    # Đường dẫn đầy đủ của app
    name = 'apps.promotions'

    # Tên hiển thị trong Django Admin
    verbose_name = 'Khuyến mãi'
