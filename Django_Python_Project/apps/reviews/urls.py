from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('add/<slug:product_slug>/', views.add_review, name='add'),
    path('edit/<int:review_id>/', views.edit_review, name='edit'),
    path('delete/<int:review_id>/', views.delete_review, name='delete'),
    path('product/<slug:product_slug>/', views.product_reviews, name='product_list'),
    path('helpful/<int:review_id>/', views.mark_helpful, name='mark_helpful'),
]