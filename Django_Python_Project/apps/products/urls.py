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
    path('search/', views.search, name='search'),

    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/ids/', views.get_wishlist_ids, name='wishlist_ids'),

    # Sentiment-based Recommendations
    path('recommended/', views.recommended_products, name='recommended'),
    path('by-sentiment/', views.products_by_sentiment, name='by_sentiment'),
    path('api/top-rated/', views.top_rated_by_sentiment, name='api_top_rated'),
    path('api/sentiment-warning/<int:product_id>/', views.sentiment_warning, name='sentiment_warning'),
]
