"""
URL patterns cho Admin Dashboard
"""
from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),

    # Products
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/create/', views.ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_edit'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),

    # Orders
    path('orders/', views.OrderListView.as_view(), name='order_list'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('orders/<int:pk>/status/', views.OrderStatusUpdateView.as_view(), name='order_status'),

    # Users
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/edit/', views.UserUpdateView.as_view(), name='user_edit'),

    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),

    # Brands
    path('brands/', views.BrandListView.as_view(), name='brand_list'),
    path('brands/create/', views.BrandCreateView.as_view(), name='brand_create'),
    path('brands/<int:pk>/edit/', views.BrandUpdateView.as_view(), name='brand_edit'),
    path('brands/<int:pk>/delete/', views.BrandDeleteView.as_view(), name='brand_delete'),

    # Reviews
    path('reviews/', views.ReviewListView.as_view(), name='review_list'),
    path('reviews/<int:pk>/approve/', views.ReviewApproveView.as_view(), name='review_approve'),
    path('reviews/<int:pk>/reject/', views.ReviewRejectView.as_view(), name='review_reject'),
    path('reviews/<int:pk>/delete/', views.ReviewDeleteView.as_view(), name='review_delete'),
    path('reviews/<int:pk>/detail/', views.ReviewDetailAPIView.as_view(), name='review_detail_api'),

    # Promotions - Vouchers
    path('vouchers/', views.VoucherListView.as_view(), name='voucher_list'),
    path('vouchers/create/', views.VoucherCreateView.as_view(), name='voucher_create'),

    # Promotions - Flash Sales
    path('flash-sales/', views.FlashSaleListView.as_view(), name='flash_sale_list'),
    path('flash-sales/create/', views.FlashSaleCreateView.as_view(), name='flash_sale_create'),
    path('flash-sales/batch/', views.FlashSaleBatchCreateView.as_view(), name='flash_sale_batch'),

    # Notifications
    path('notifications/', views.NotificationListView.as_view(), name='notification_list'),
    path('notifications/create/', views.NotificationCreateView.as_view(), name='notification_create'),
    path('notifications/<int:pk>/delete/', views.NotificationDeleteView.as_view(), name='notification_delete'),
    path('notifications/bulk-action/', views.NotificationBulkActionView.as_view(), name='notification_bulk_action'),

    # API Endpoints
    path('api/chart-data/', views.ChartDataView.as_view(), name='chart_data'),
    path('api/revenue-report/', views.RevenueReportView.as_view(), name='revenue_report_api'),
    path('revenue-report/', views.RevenueReportPageView.as_view(), name='revenue_report'),
]
