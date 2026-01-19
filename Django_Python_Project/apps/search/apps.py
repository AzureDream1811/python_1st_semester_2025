"""
App Configuration cho Search App - ElectroShop

Search app xử lý tìm kiếm sản phẩm với các tính năng:
- Tìm kiếm full-text tiếng Việt (có dấu và không dấu)
- Autocomplete gợi ý tìm kiếm
- Lọc theo danh mục, giá, thương hiệu
- Ghi log lịch sử tìm kiếm để phân tích
"""
from django.apps import AppConfig


class SearchConfig(AppConfig):
    """
    Cấu hình cho Search App
    
    Attributes:
        default_auto_field: Kiểu field mặc định cho primary key
        name: Tên đầy đủ của app (dùng trong INSTALLED_APPS)
        verbose_name: Tên hiển thị trong admin
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.search'
    verbose_name = 'Tìm kiếm'
