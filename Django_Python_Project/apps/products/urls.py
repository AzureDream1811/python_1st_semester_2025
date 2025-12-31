"""
URLs for products app
"""
from django.urls import path
from . import views


app_name = 'products'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='detail'),
    path('category/<slug:slug>/', views.category_products, name='category'),
]
