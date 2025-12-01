from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('products/', views.product_list_view, name='list'),
    path('product/<slug:slug>/', views.product_detail_view, name='detail'),
    path('category/<slug:slug>/', views.category_view, name='category'),
    path('search/', views.search_view, name='search'),
    path('ajax/search/', views.ajax_search, name='ajax_search'),
    
    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
]
