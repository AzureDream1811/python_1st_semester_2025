"""
URLs for cart app
"""
from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='detail'),
    path('add/<int:product_id>/', views.add_to_cart, name='add'),
    path('update/<int:item_id>/', views.update_cart, name='update'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove'),
    path('remove-voucher/', views.remove_voucher, name='remove_voucher'),
    path('save-later/<int:item_id>/', views.toggle_save_for_later, name='save_for_later'),
    path('move-to-cart/<int:item_id>/', views.move_to_cart, name='move_to_cart'),
    path('add-to-wishlist/<int:item_id>/', views.add_to_wishlist_from_cart, name='add_to_wishlist'),
]
