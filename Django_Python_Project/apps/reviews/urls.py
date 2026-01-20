"""
URLs for reviews app
"""
from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('add/<slug:product_slug>/', views.add_review, name='add'),
    path('product/<slug:product_slug>/', views.product_reviews, name='product_reviews'),
    path('helpful/<int:review_id>/', views.mark_helpful, name='helpful'),
    path('edit/<int:review_id>/', views.edit_review, name='edit'),
    path('get/<int:review_id>/', views.get_review, name='get'),
]
