"""
URL Configuration cho Search App - ElectroShop
"""
from django.urls import path
# from . import views

app_name = 'search'

urlpatterns = [
    # Trang kết quả tìm kiếm chính
    # URL: /search/?q=<query>&category=<slug>&...
    path('', views.search_products, name='search'),

    # API autocomplete - gợi ý khi user đang gõ
    # URL: /search/autocomplete/?q=<query>&limit=<int>
    path('autocomplete/', views.autocomplete, name='autocomplete'),

    # API từ khóa phổ biến - hiển thị khi chưa nhập gì
    # URL: /search/suggestions/
    path('suggestions/', views.search_suggestions, name='suggestions'),
]
