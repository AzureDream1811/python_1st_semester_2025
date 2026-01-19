"""
App Configuration cho Recommendations - ElectroShop
===================================================

Cấu hình Django app cho module gợi ý sản phẩm.

Module này quản lý:
- Theo dõi hoạt động người dùng
- Tính toán độ tương đồng sản phẩm
- Gợi ý sản phẩm cá nhân hóa
- Phân tích xu hướng mua sắm

Tác giả: ElectroShop Team
"""
from django.apps import AppConfig


class RecommendationsConfig(AppConfig):
    """
    Cấu hình cho app Recommendations
    
    Attributes:
        default_auto_field: Kiểu primary key mặc định
        name: Đường dẫn đầy đủ của app
        verbose_name: Tên hiển thị trong Admin (tiếng Việt)
    """
    # Sử dụng BigAutoField cho primary key (hỗ trợ số lượng lớn)
    default_auto_field = 'django.db.models.BigAutoField'

    # Đường dẫn đầy đủ của app
    name = 'apps.recommendations'

    # Tên hiển thị trong Django Admin
    verbose_name = 'Gợi ý sản phẩm'
