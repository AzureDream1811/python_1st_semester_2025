from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    # Add review
    path('add/<slug:product_slug>/', views.add_review, name='add'),

    # Edit review
    path('edit/<int:review_id>/', views.edit_review, name='edit'),

    # Delete review
    path('delete/<int:review_id>/', views.delete_review, name='delete'),

    # Product reviews list (trang riêng xem tất cả reviews)
    path('product/<slug:product_slug>/', views.product_reviews, name='product_list'),

    # Mark helpful
    path('helpful/<int:review_id>/', views.mark_helpful, name='mark_helpful'),
]
