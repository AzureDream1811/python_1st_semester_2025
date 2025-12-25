from django.urls import path
from . import views

app_name = 'promotions'

urlpatterns = [
    path('flash-sales/', views.flash_sale_list, name='flash_sales'),
    path('flash-sales/<int:pk>/', views.flash_sale_detail, name='flash_sale_detail'),
    path('combo-deals/', views.combo_deal_list, name='combo_deals'),
    path('my-vouchers/', views.my_vouchers, name='my_vouchers'),
    path('validate-voucher/', views.validate_voucher, name='validate_voucher'),
    path('apply-voucher/', views.apply_voucher, name='apply_voucher'),
]
