"""
Notification Service for ElectroShop
Handles sending realtime and push notifications
"""
from typing import Optional, Dict, Any, List
from django.contrib.auth.models import User
from django.db.models import QuerySet
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from apps.notifications.models import Notification, PushSubscription, NotificationPreference


class NotificationService:
    """Service class for managing notifications"""

    def __init__(self):
        self.channel_layer = get_channel_layer()

    # === REALTIME NOTIFICATIONS ===

    def send_realtime(self, user_id: int, notification_type: str, data: Dict[str, Any]) -> None:
        """
        Send realtime notification via WebSocket
        Property 1: Notification must be created when order status changes
        """
        if self.channel_layer:
            async_to_sync(self.channel_layer.group_send)(
                f'notifications_{user_id}',
                {
                    'type': 'notification_message',
                    'notification_type': notification_type,
                    'data': data
                }
            )

    def create_notification(
            self,
            user: User,
            notification_type: str,
            title: str,
            message: str,
            data: Optional[Dict] = None,
            url: str = ''
    ) -> Notification:
        """Create a new notification and send realtime update"""
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            data=data or {},
            url=url
        )

        # Send realtime notification
        self.send_realtime(user.id, notification_type, {
            'id': notification.id,
            'title': title,
            'message': message,
            'url': url,
            'created_at': notification.created_at.isoformat()
        })

        return notification

    # === UNREAD COUNT ===

    def get_unread_count(self, user_id: int) -> int:
        """
        Get count of unread notifications
        Property 2: Count must equal actual unread notifications in DB
        """
        return Notification.objects.filter(
            user_id=user_id,
            is_read=False
        ).count()

    def get_unread_notifications(self, user_id: int, limit: int = 10) -> QuerySet:
        """Get unread notifications for user"""
        return Notification.objects.filter(
            user_id=user_id,
            is_read=False
        ).order_by('-created_at')[:limit]

    # === MARK AS READ ===

    def mark_as_read(self, notification_id: int) -> bool:
        """
        Mark notification as read
        Property 3: is_read must change from False to True
        """
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.mark_as_read()
            return True
        except Notification.DoesNotExist:
            return False

    def mark_all_as_read(self, user_id: int) -> int:
        """Mark all notifications as read for user"""
        from django.utils import timezone
        return Notification.objects.filter(
            user_id=user_id,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())

    # === PUSH NOTIFICATIONS ===

    def send_push(self, user_id: int, title: str, body: str, data: Optional[Dict] = None) -> bool:
        """Send push notification via Firebase Cloud Messaging"""
        from django.conf import settings

        subscriptions = PushSubscription.objects.filter(
            user_id=user_id,
            is_active=True
        )

        if not subscriptions.exists():
            return False

        # TODO: Implement FCM push notification
        # This requires firebase-admin setup
        try:
            # Placeholder for FCM implementation
            for subscription in subscriptions:
                # Send to each subscription endpoint
                pass
            return True
        except Exception:
            return False

    # === ORDER STATUS NOTIFICATIONS ===

    def notify_order_status_change(self, order, old_status=None) -> Optional[Notification]:
        """
        Send notification when order status changes
        Property 1: Must create notification for order owner
        """
        if not order.user:
            return None

        status_config = {
            'pending': {
                'title': 'Đặt hàng thành công!',
                'message': f'Đơn hàng #{order.order_number} đã được đặt thành công. Đang chờ xác nhận từ cửa hàng.',
                'icon': 'clock'
            },
            'confirmed': {
                'title': 'Đơn hàng đã được xác nhận',
                'message': f'Cửa hàng đã xác nhận và tiếp nhận đơn hàng #{order.order_number} của bạn.',
                'icon': 'check-circle'
            },
            'processing': {
                'title': 'Đang chuẩn bị hàng',
                'message': f'Đơn hàng #{order.order_number} đang được đóng gói và chuẩn bị giao cho đơn vị vận chuyển.',
                'icon': 'box-seam'
            },
            'shipping': {
                'title': 'Đơn hàng đang được giao',
                'message': f'Đơn hàng #{order.order_number} đang trên đường giao đến bạn. Vui lòng chú ý điện thoại.',
                'icon': 'truck'
            },
            'delivered': {
                'title': 'Đã giao hàng thành công',
                'message': f'Đơn hàng #{order.order_number} đã được giao thành công. Cảm ơn bạn đã mua hàng!',
                'icon': 'bag-check'
            },
            'completed': {
                'title': 'Đơn hàng hoàn thành',
                'message': f'Đơn hàng #{order.order_number} đã hoàn thành. Cảm ơn bạn đã tin tưởng ElectroShop!',
                'icon': 'check-circle-fill'
            },
            'cancelled': {
                'title': 'Đơn hàng đã bị hủy',
                'message': f'Đơn hàng #{order.order_number} đã bị hủy.',
                'icon': 'x-circle'
            },
            'refunded': {
                'title': 'Đã hoàn tiền',
                'message': f'Đơn hàng #{order.order_number} đã được hoàn tiền thành công. Tiền sẽ được chuyển về tài khoản của bạn.',
                'icon': 'cash-coin'
            },
        }

        config = status_config.get(order.status)
        if not config:
            return None

        return self.create_notification(
            user=order.user,
            notification_type='order',
            title=config['title'],
            message=config['message'],
            data={
                'order_id': order.id,
                'order_number': order.order_number,
                'status': order.status,
                'old_status': old_status,
                'icon': config['icon']
            },
            url=f'/orders/{order.order_number}/'
        )

    # === WISHLIST PRICE DROP ===

    def notify_wishlist_price_drop(self, product, old_price, new_price) -> List[Notification]:
        """
        Notify users when wishlist product price drops
        Property 4: Must notify all users with product in wishlist
        """
        from apps.products.models import WishlistItem

        notifications = []
        wishlist_items = WishlistItem.objects.filter(
            product=product
        ).select_related('user')

        discount_percent = int((old_price - new_price) / old_price * 100)

        for item in wishlist_items:
            # Check user preferences
            try:
                prefs = item.user.notification_preferences
                if not prefs.push_wishlist:
                    continue
            except NotificationPreference.DoesNotExist:
                pass

            notification = self.create_notification(
                user=item.user,
                notification_type='wishlist',
                title=f'🔥 {product.name} giảm giá {discount_percent}%!',
                message=f'Sản phẩm trong wishlist của bạn đã giảm từ {old_price:,.0f}đ xuống {new_price:,.0f}đ',
                data={
                    'product_id': product.id,
                    'old_price': float(old_price),
                    'new_price': float(new_price)
                },
                url=f'/products/{product.slug}/'
            )
            notifications.append(notification)

        return notifications

    # === PROMOTION NOTIFICATIONS ===

    def notify_new_promotion(self, promotion, users: Optional[QuerySet] = None) -> int:
        """Notify users about new promotion"""
        if users is None:
            users = User.objects.filter(is_active=True)

        count = 0
        for user in users:
            self.create_notification(
                user=user,
                notification_type='promotion',
                title=f'🎁 {promotion.name}',
                message=promotion.description,
                data={'promotion_id': promotion.id},
                url='/promotions/'
            )
            count += 1

        return count
