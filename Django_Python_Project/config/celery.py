"""
Celery Configuration for ElectroShop
Background task processing for notifications, analytics, shipping sync, etc.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Create Celery app
app = Celery('electroshop')

# Load config from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()

# Celery Beat Schedule - Periodic Tasks
app.conf.beat_schedule = {
    # Sync shipping status every 30 minutes
    'sync-shipping-status': {
        'task': 'apps.shipping.tasks.sync_all_shipping_status',
        'schedule': crontab(minute='*/30'),
    },
    # Check low stock every hour
    'check-low-stock': {
        'task': 'apps.shipping.tasks.check_low_stock_alert',
        'schedule': crontab(minute=0, hour='*/1'),
    },
    # Update recommendation model daily at 2 AM
    'update-recommendations': {
        'task': 'apps.recommendations.tasks.update_recommendation_model',
        'schedule': crontab(minute=0, hour=2),
    },
    # Clean old notifications weekly
    'clean-old-notifications': {
        'task': 'apps.notifications.tasks.clean_old_notifications',
        'schedule': crontab(minute=0, hour=3, day_of_week=0),
    },
}

app.conf.timezone = 'Asia/Ho_Chi_Minh'


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery"""
    print(f'Request: {self.request!r}')
