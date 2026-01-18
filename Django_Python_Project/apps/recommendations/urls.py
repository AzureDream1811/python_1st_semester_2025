"""
URL Configuration cho Recommendations App - ElectroShop
=======================================================

Định nghĩa các API endpoints cho hệ thống gợi ý sản phẩm:
- Gợi ý cá nhân hóa cho user
- Sản phẩm tương tự
- Sản phẩm thường mua cùng
- Sản phẩm trending
- Ghi nhận hoạt động người dùng

Tác giả: ElectroShop Team
"""
from django.urls import path
from . import views

# Namespace cho app recommendations
# Sử dụng: {% url 'recommendations:similar_products' product_id=1 %}
app_name = 'recommendations'

urlpatterns = [
    # =========================================================================
    # GỢI Ý CÁ NHÂN HÓA
    # =========================================================================

    # Gợi ý cho user cụ thể (theo user_id)
    # URL: /recommendations/api/user/1/
    path(
        'api/user/<int:user_id>/',
        views.get_recommendations_for_user,
        name='user_recommendations'
    ),

    # Gợi ý cho user hiện tại (đang đăng nhập)
    # URL: /recommendations/api/user/
    path(
        'api/user/',
        views.get_recommendations_for_user,
        name='current_user_recommendations'
    ),

    # =========================================================================
    # SẢN PHẨM TƯƠNG TỰ
    # =========================================================================

    # Lấy sản phẩm tương tự với sản phẩm đang xem
    # URL: /recommendations/api/similar/1/
    path(
        'api/similar/<int:product_id>/',
        views.get_similar_products,
        name='similar_products'
    ),

    # =========================================================================
    # SẢN PHẨM THƯỜNG MUA CÙNG
    # =========================================================================

    # Lấy sản phẩm thường được mua cùng
    # URL: /recommendations/api/frequently-bought-together/1/
    path(
        'api/frequently-bought-together/<int:product_id>/',
        views.get_frequently_bought_together,
        name='frequently_bought_together'
    ),

    # =========================================================================
    # SẢN PHẨM TRENDING
    # =========================================================================

    # Lấy sản phẩm đang trending (7 ngày gần nhất)
    # URL: /recommendations/api/trending/
    path(
        'api/trending/',
        views.trending_products,
        name='trending_products'
    ),

    # =========================================================================
    # GHI NHẬN HOẠT ĐỘNG
    # =========================================================================

    # API ghi nhận hoạt động người dùng (POST)
    # URL: /recommendations/api/log-activity/
    path(
        'api/log-activity/',
        views.log_user_activity,
        name='log_activity'
    ),
]
