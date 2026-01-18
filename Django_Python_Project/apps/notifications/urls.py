from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='list'),
    path('unread-count/', views.unread_count, name='unread_count'),
    path('<int:pk>/mark-read/', views.mark_as_read, name='mark_read'),
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('<int:pk>/delete/', views.delete_notification, name='delete'),
    path('preferences/', views.notification_preferences, name='preferences'),
]
