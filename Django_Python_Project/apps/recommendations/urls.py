"""
Recommendations URLs for ElectroShop
API endpoints for product recommendations
"""
from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    # API endpoints
    path('api/user/<int:user_id>/', views.get_recommendations_for_user, name='user_recommendations'),
    path('api/user/', views.get_recommendations_for_user, name='current_user_recommendations'),
    path('api/similar/<int:product_id>/', views.get_similar_products, name='similar_products'),
    path('api/frequently-bought-together/<int:product_id>/', views.get_frequently_bought_together,
         name='frequently_bought_together'),
    path('api/trending/', views.trending_products, name='trending_products'),
    path('api/log-activity/', views.log_user_activity, name='log_activity'),
]
