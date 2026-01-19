"""
URLs for orders app
"""
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('', views.order_list, name='list'),
    path('<str:order_number>/', views.order_detail, name='detail'),
    path('<str:order_number>/cancel/', views.cancel_order, name='cancel'),
    path('<str:order_number>/rebuy/', views.rebuy_order, name='rebuy'),
    path('<str:order_number>/rebuy/<int:item_id>/', views.rebuy_item, name='rebuy_item'),
    path('api/check-payment-status/', views.check_payment_status, name='check_payment_status'),
]
