from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    # Tạo review
    path('create/<slug:product_slug>/', views.create_review_view, name='create'),
    path('create/<slug:product_slug>/<int:order_item_id>/', views.create_review_view, name='create_from_order'),
    
    # Xem reviews
    path('product/<slug:product_slug>/', views.product_reviews_view, name='product_reviews'),
    path('my-reviews/', views.my_reviews_view, name='my_reviews'),
    path('pending/', views.pending_reviews_view, name='pending'),
    
    # Edit/Delete
    path('edit/<int:review_id>/', views.edit_review_view, name='edit'),
    path('delete/<int:review_id>/', views.delete_review_view, name='delete'),
    
    # Helpful
    path('helpful/<int:review_id>/', views.mark_helpful_view, name='mark_helpful'),
    
    # API
    path('api/analyze/', views.analyze_sentiment_api, name='analyze_api'),
]
