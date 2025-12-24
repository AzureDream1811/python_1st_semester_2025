"""
URLs for products app
"""
from django.urls import path
from . import views


app_name = 'products'

urlpatterns = [
    path('', views.home, name='home'),
    path('search-result/<str:name>/', views.search_result, name='search-result'),
    # Trang chủ - danh sách sản phẩm
    # path('', views.product_list, name='product_list'),
    # path('product/<int:pk>/', views.product_detail, name='product_detail'),
]
