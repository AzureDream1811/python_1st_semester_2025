from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Notification, NotificationPreference
from .services.notification_service import NotificationService

notification_service = NotificationService()


@login_required
def notification_list(request):
    """Danh sách thông báo của user"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

    # Filter by type
    notification_type = request.GET.get('type')
    if notification_type:
        notifications = notifications.filter(notification_type=notification_type)

    # Filter by read status
    is_read = request.GET.get('is_read')
    if is_read == 'true':
        notifications = notifications.filter(is_read=True)
    elif is_read == 'false':
        notifications = notifications.filter(is_read=False)

    paginator = Paginator(notifications, 20)
    page = request.GET.get('page', 1)
    notifications = paginator.get_page(page)

    unread_count = notification_service.get_unread_count(request.user.id)

    context = {
        'notifications': notifications,
        'unread_count': unread_count,
        'notification_types': ['order', 'promotion', 'wishlist', 'system'],
    }
    return render(request, 'notifications/notification_list.html', context)


@login_required
def unread_count(request):
    """API: Lấy số thông báo chưa đọc"""
    count = notification_service.get_unread_count(request.user.id)
    return JsonResponse({'unread_count': count})


@login_required
def mark_as_read(request, pk):
    """Đánh dấu thông báo đã đọc"""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification_service.mark_as_read(pk)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    return redirect('notifications:list')


@login_required
def mark_all_read(request):
    """Đánh dấu tất cả thông báo đã đọc"""
    if request.method == 'POST':
        notification_service.mark_all_as_read(request.user.id)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

        messages.success(request, 'Đã đánh dấu tất cả thông báo là đã đọc.')

    return redirect('notifications:list')


@login_required
def delete_notification(request, pk):
    """Xóa thông báo"""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    messages.success(request, 'Đã xóa thông báo.')
    return redirect('notifications:list')


@login_required
def notification_preferences(request):
    """Cài đặt thông báo"""
    preference, created = NotificationPreference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        errors = []
        warnings = []

        # Get form values
        email_order_updates = request.POST.get('email_order_updates') == 'on'
        email_promotions = request.POST.get('email_promotions') == 'on'
        email_wishlist = request.POST.get('email_wishlist') == 'on'
        email_newsletter = request.POST.get('email_newsletter') == 'on'
        email_account = True  # Required - cannot be disabled

        push_order_updates = request.POST.get('push_order_updates') == 'on'
        push_promotions = request.POST.get('push_promotions') == 'on'
        push_wishlist = request.POST.get('push_wishlist') == 'on'
        push_chat = request.POST.get('push_chat') == 'on'
        push_flash_sale = request.POST.get('push_flash_sale') == 'on'
        push_delivery = request.POST.get('push_delivery') == 'on'

        sms_order_confirmation = request.POST.get('sms_order_confirmation') == 'on'
        sms_delivery = request.POST.get('sms_delivery') == 'on'

        # Validation: at least one order notification channel
        order_channels = [email_order_updates, push_order_updates, sms_order_confirmation]
        if not any(order_channels):
            warnings.append(
                'Khuyến nghị bật ít nhất 1 kênh nhận thông báo đơn hàng để theo dõi trạng thái đơn hàng của bạn.')

        # Validation: marketing frequency warning
        marketing_channels = [email_promotions, email_newsletter, push_promotions, push_flash_sale]
        if sum(marketing_channels) >= 4:
            warnings.append('Bạn đã bật nhiều kênh nhận khuyến mãi. Bạn có thể nhận nhiều thông báo trong ngày.')

        # Save preferences
        preference.email_order_updates = email_order_updates
        preference.email_promotions = email_promotions
        preference.email_wishlist = email_wishlist
        preference.email_newsletter = email_newsletter
        preference.email_account = email_account

        preference.push_order_updates = push_order_updates
        preference.push_promotions = push_promotions
        preference.push_wishlist = push_wishlist
        preference.push_chat = push_chat
        preference.push_flash_sale = push_flash_sale
        preference.push_delivery = push_delivery

        preference.sms_order_confirmation = sms_order_confirmation
        preference.sms_delivery = sms_delivery

        preference.save()

        for warning in warnings:
            messages.warning(request, warning)

        messages.success(request, 'Đã cập nhật cài đặt thông báo.')
        return redirect('notifications:preferences')

    # Group preferences for template
    preference_groups = {
        'transactional': {
            'title': 'Giao dịch',
            'icon': 'bi-box-seam',
            'description': 'Thông báo về đơn hàng và giao dịch của bạn',
            'items': [
                {'id': 'email_order_updates', 'label': 'Email cập nhật đơn hàng',
                 'desc': 'Nhận email khi đơn hàng thay đổi trạng thái', 'value': preference.email_order_updates},
                {'id': 'push_order_updates', 'label': 'Push cập nhật đơn hàng',
                 'desc': 'Nhận thông báo khi đơn hàng thay đổi trạng thái', 'value': preference.push_order_updates},
                {'id': 'push_delivery', 'label': 'Push giao hàng',
                 'desc': 'Nhận thông báo realtime khi shipper đang giao', 'value': preference.push_delivery},
                {'id': 'sms_order_confirmation', 'label': 'SMS xác nhận đơn hàng',
                 'desc': 'Nhận SMS xác nhận đơn hàng đã được đặt', 'value': preference.sms_order_confirmation,
                 'note': 'Có thể phát sinh phí SMS'},
                {'id': 'sms_delivery', 'label': 'SMS giao hàng', 'desc': 'Nhận SMS khi đơn hàng sắp được giao',
                 'value': preference.sms_delivery, 'note': 'Có thể phát sinh phí SMS'},
            ]
        },
        'marketing': {
            'title': 'Khuyến mãi & Ưu đãi',
            'icon': 'bi-gift',
            'description': 'Nhận thông báo về chương trình khuyến mãi',
            'items': [
                {'id': 'email_promotions', 'label': 'Email khuyến mãi', 'desc': 'Nhận email về flash sale, voucher mới',
                 'value': preference.email_promotions},
                {'id': 'email_newsletter', 'label': 'Email bản tin', 'desc': 'Nhận bản tin hàng tuần về sản phẩm mới',
                 'value': preference.email_newsletter},
                {'id': 'push_promotions', 'label': 'Push khuyến mãi', 'desc': 'Nhận thông báo về khuyến mãi',
                 'value': preference.push_promotions},
                {'id': 'push_flash_sale', 'label': 'Push Flash Sale',
                 'desc': 'Nhận thông báo khi Flash Sale sắp bắt đầu', 'value': preference.push_flash_sale},
            ]
        },
        'personalized': {
            'title': 'Cá nhân hóa',
            'icon': 'bi-heart',
            'description': 'Thông báo dựa trên sở thích của bạn',
            'items': [
                {'id': 'email_wishlist', 'label': 'Email Wishlist',
                 'desc': 'Nhận email khi sản phẩm yêu thích giảm giá', 'value': preference.email_wishlist},
                {'id': 'push_wishlist', 'label': 'Push Wishlist',
                 'desc': 'Nhận thông báo khi sản phẩm yêu thích giảm giá', 'value': preference.push_wishlist},
            ]
        },
        'communication': {
            'title': 'Giao tiếp',
            'icon': 'bi-chat-dots',
            'description': 'Tin nhắn và hỗ trợ khách hàng',
            'items': [
                {'id': 'push_chat', 'label': 'Push Chat', 'desc': 'Nhận thông báo khi có tin nhắn mới từ hỗ trợ',
                 'value': preference.push_chat},
            ]
        },
        'security': {
            'title': 'Bảo mật',
            'icon': 'bi-shield-lock',
            'description': 'Thông báo quan trọng về tài khoản',
            'required': True,
            'items': [
                {'id': 'email_account', 'label': 'Email tài khoản',
                 'desc': 'Thông báo về bảo mật, thay đổi mật khẩu, đăng nhập', 'value': preference.email_account,
                 'required': True},
            ]
        },
    }

    return render(request, 'notifications/preferences.html', {
        'preference': preference,
        'preference_groups': preference_groups
    })
