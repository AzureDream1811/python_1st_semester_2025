from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('success/<str:order_number>/', views.order_success_view, name='success'),
    path('my-orders/', views.order_list_view, name='list'),
    path('my-orders/<str:order_number>/', views.order_detail_view, name='detail'),
    path('cancel/<str:order_number>/', views.cancel_order_view, name='cancel'),
    path('track/', views.track_order_view, name='track'),
]
