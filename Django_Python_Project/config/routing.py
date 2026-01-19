"""
WebSocket URL routing for ElectroShop

Cấu hình routing cho WebSocket connections:
- Notifications: Real-time thông báo cho user
"""
from django.urls import path

websocket_urlpatterns = []

try:
    from apps.notifications.consumers import NotificationConsumer
    
    websocket_urlpatterns = [
        path('ws/notifications/', NotificationConsumer.as_asgi()),
    ]
except ImportError:
    pass
