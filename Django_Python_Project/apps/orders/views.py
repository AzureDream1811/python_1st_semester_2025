import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Order, OrderItem, OrderHistory
from apps.cart.views import get_or_create_cart


def get_smart_image_url(image_field):
    """
    Lấy URL đúng cho image field.
    Nếu path đã là URL đầy đủ (http/https), trả về trực tiếp.
    Nếu không, trả về .url như bình thường.
    """
    if not image_field:
        return ''

    image_name = str(image_field.name) if hasattr(image_field, 'name') else str(image_field)

    if image_name.startswith(('http://', 'https://')):
        return image_name

    try:
        return image_field.url
    except (ValueError, AttributeError):
        return ''


@login_required
def checkout(request):
    """Trang thanh toán"""
    cart = get_or_create_cart(request)
    # Chỉ lấy items chưa được đánh dấu "thanh toán sau"
    items = cart.items.filter(saved_for_later=False).select_related('product')

    if not items.exists():
        messages.warning(request, 'Giỏ hàng trống. Vui lòng thêm sản phẩm.')
        return redirect('cart:detail')

    # Kiểm tra tồn kho trước khi cho phép checkout
    stock_errors = []
    for item in items:
        if item.quantity > item.product.stock:
            stock_errors.append({
                'product': item.product,
                'requested': item.quantity,
                'available': item.product.stock
            })

    if stock_errors:
        for error in stock_errors:
            if error['available'] == 0:
                messages.error(request, f'Sản phẩm "{error["product"].name}" đã hết hàng.')
            else:
                messages.error(request,
                               f'Sản phẩm "{error["product"].name}" chỉ còn {error["available"]} trong kho (bạn đang đặt {error["requested"]}).')
        return render(request, 'orders/checkout.html', {
            'cart': cart,
            'items': items,
            'stock_errors': stock_errors,
        })

    if request.method == 'POST':
        # Kiểm tra có chọn địa chỉ đã lưu không
        selected_address_id = request.POST.get('selected_address', '')

        if selected_address_id:
            # Sử dụng địa chỉ đã lưu
            from apps.accounts.models import Address
            try:
                saved_addr = Address.objects.get(pk=selected_address_id, user=request.user)
                full_name = saved_addr.full_name
                phone = saved_addr.phone
                address = saved_addr.address
                city = saved_addr.province
                city_code = saved_addr.province_code
                district = saved_addr.district
                district_code = saved_addr.district_code
                ward = saved_addr.ward
                ward_code = saved_addr.ward_code
                email = request.POST.get('email', request.user.email).strip()
            except Address.DoesNotExist:
                messages.error(request, 'Địa chỉ không tồn tại.')
                return redirect('orders:checkout')
        else:
            # Nhập địa chỉ mới
            full_name = request.POST.get('full_name', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()
            address = request.POST.get('address', '').strip()
            district = request.POST.get('district', '').strip()
            city = request.POST.get('city', '').strip()
            ward = request.POST.get('ward', '').strip()
            city_code = request.POST.get('city_code', '').strip()
            district_code = request.POST.get('district_code', '').strip()
            ward_code = request.POST.get('ward_code', '').strip()

        note = request.POST.get('note', '').strip()
        payment_method = request.POST.get('payment_method', 'cod')
        save_address = request.POST.get('save_address') == '1'

        if not all([full_name, email, phone, address, district, city]):
            messages.error(request, 'Vui lòng điền đầy đủ thông tin giao hàng.')
            return render(request, 'orders/checkout.html', {
                'cart': cart,
                'items': items,
            })

        with transaction.atomic():
            # Lưu địa chỉ mới vào sổ địa chỉ nếu được chọn (và set làm mặc định)
            if save_address and not selected_address_id:
                from apps.accounts.models import Address
                # Bỏ mặc định các địa chỉ cũ
                Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
                # Tạo địa chỉ mới làm mặc định
                Address.objects.create(
                    user=request.user,
                    full_name=full_name,
                    phone=phone,
                    address=address,
                    province=city,
                    province_code=city_code,
                    district=district,
                    district_code=district_code,
                    ward=ward,
                    ward_code=ward_code,
                    is_default=True
                )

            # Tạo Order
            order_number = request.session.get('draft_order_number') or Order.generate_order_number()
            if Order.objects.filter(order_number=order_number).exists():
                order_number = Order.generate_order_number()
                request.session['draft_order_number'] = order_number
            order = Order.objects.create(
                order_number=order_number,
                user=request.user,
                full_name=full_name,
                email=email,
                phone=phone,
                address=address,
                ward=ward,
                district=district,
                city=city,
                note=note,
                payment_method=payment_method,
                subtotal=cart.subtotal,
                total=cart.total,
            )

            # Transfer cart items sang order items và giảm stock
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    product_image=get_smart_image_url(item.product.image),
                    price=item.price,
                    quantity=item.quantity,
                )

                # Giảm stock
                item.product.stock -= item.quantity
                item.product.sold += item.quantity
                item.product.save(update_fields=['stock', 'sold'])

            # Tạo order history
            OrderHistory.objects.create(order=order, status='pending')

            # Gửi thông báo đặt hàng thành công
            try:
                from apps.notifications.services.notification_service import NotificationService
                notification_service = NotificationService()
                notification_service.notify_order_status_change(order)
            except Exception:
                pass

            # Clear cart
            cart.clear()
            request.session.pop('draft_order_number', None)

        messages.success(request, f'Đặt hàng thành công! Mã đơn hàng: {order.order_number}')

        # Redirect dựa trên phương thức thanh toán
        if payment_method == 'bank_transfer':
            return redirect('payments:bank_transfer', order_id=order.id)
        elif payment_method == 'momo':
            return redirect('payments:momo_payment', order_id=order.id)
        elif payment_method == 'zalopay':
            return redirect('payments:zalopay_payment', order_id=order.id)
        else:
            return redirect('orders:detail', order_number=order.order_number)

    # Pre-fill từ profile
    profile = getattr(request.user, 'profile', None)

    # Lấy địa chỉ và thẻ đã lưu
    from apps.accounts.models import Address, SavedCard
    saved_addresses = Address.objects.filter(user=request.user).order_by('-is_default', '-created_at')
    saved_cards = SavedCard.objects.filter(user=request.user, is_expired=False)
    default_address = saved_addresses.filter(is_default=True).first()
    # Generate QR codes for payment methods
    from apps.payments.models import BankAccount, EWalletAccount
    from apps.payments.services.qr_service import QRService

    draft_order_number = request.session.get('draft_order_number')
    if not draft_order_number:
        draft_order_number = Order.generate_order_number()
        request.session['draft_order_number'] = draft_order_number

    transfer_phone = ''
    if default_address and default_address.phone:
        transfer_phone = default_address.phone
    elif profile and getattr(profile, 'phone', None):
        transfer_phone = profile.phone

    transfer_content = QRService.generate_transfer_content(draft_order_number, transfer_phone)

    # QR Bank Transfer
    bank_qr_url = None
    bank_account = BankAccount.objects.filter(
        is_active=True,
        bank_code='MB'
    ).order_by('-is_default').first()
    if not bank_account:
        bank_account = BankAccount.objects.filter(is_active=True, is_default=True).first()
    if not bank_account:
        bank_account = BankAccount.objects.filter(is_active=True).first()
    if not bank_account:
        bank_account = BankAccount(
            bank_code='MB',
            bank_name='MB Bank',
            account_number='123456789',
            account_name='DEMO PROJECT',
            is_active=True,
            is_default=True
        )

    if bank_account:
        bank_qr_url = QRService.generate_vietqr_url(
            bank_code=bank_account.bank_code,
            account_number=bank_account.account_number,
            amount=cart.total,
            content=transfer_content,
            account_name=bank_account.account_name
        )

    # QR MoMo
    momo_qr_base64 = None
    momo_account = EWalletAccount.objects.filter(wallet_type='momo', is_active=True, is_default=True).first()
    if not momo_account:
        momo_account = EWalletAccount.objects.filter(wallet_type='momo', is_active=True).first()
    if not momo_account:
        momo_account = EWalletAccount(
            wallet_type='momo',
            wallet_id='0900000000',
            wallet_name='DEMO MOMO',
            is_active=True,
            is_default=True
        )

    if momo_account:
        momo_data = QRService.generate_momo_qr(
            phone=momo_account.wallet_id,
            amount=cart.total,
            content=transfer_content
        )
        momo_qr_base64 = momo_data.get('qr_base64')

    # QR ZaloPay
    zalopay_qr_base64 = None
    zalopay_account = EWalletAccount.objects.filter(wallet_type='zalopay', is_active=True, is_default=True).first()
    if not zalopay_account:
        zalopay_account = EWalletAccount.objects.filter(wallet_type='zalopay', is_active=True).first()
    if not zalopay_account:
        zalopay_account = EWalletAccount(
            wallet_type='zalopay',
            wallet_id='0900000000',
            wallet_name='DEMO ZALOPAY',
            is_active=True,
            is_default=True
        )

    if zalopay_account:
        zalopay_data = QRService.generate_zalopay_qr(
            wallet_id=zalopay_account.wallet_id,
            amount=cart.total,
            content=transfer_content
        )
        zalopay_qr_base64 = zalopay_data.get('qr_base64')

    context = {
        'cart': cart,
        'items': items,
        'profile': profile,
        'saved_addresses': saved_addresses,
        'saved_cards': saved_cards,
        'default_address': default_address,
        'transfer_content': transfer_content,
        'bank_account': bank_account,
        'bank_qr_url': bank_qr_url,
        'momo_account': momo_account,
        'momo_qr_base64': momo_qr_base64,
        'zalopay_account': zalopay_account,
        'zalopay_qr_base64': zalopay_qr_base64,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
def order_list(request):
    """Danh sách đơn hàng của user"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    # Pagination
    paginator = Paginator(orders, 10)
    page = request.GET.get('page', 1)
    orders = paginator.get_page(page)

    context = {
        'orders': orders,
    }
    return render(request, 'orders/order_list.html', context)


@login_required
def order_detail(request, order_number):
    """Chi tiết đơn hàng"""
    order = get_object_or_404(
        Order.objects.prefetch_related('items', 'history'),
        order_number=order_number,
        user=request.user
    )

    context = {
        'order': order,
    }
    return render(request, 'orders/order_detail.html', context)


@login_required
def cancel_order(request, order_number):
    """Hủy đơn hàng"""
    order = get_object_or_404(
        Order,
        order_number=order_number,
        user=request.user
    )

    if not order.can_cancel():
        messages.error(request, 'Không thể hủy đơn hàng này.')
        return redirect('orders:detail', order_number=order_number)

    with transaction.atomic():
        # Restore stock
        for item in order.items.all():
            if item.product:
                item.product.stock += item.quantity
                item.product.sold -= item.quantity
                item.product.save(update_fields=['stock', 'sold'])

        # Update order status
        order.status = 'cancelled'
        order.save(update_fields=['status'])

        # Add history
        OrderHistory.objects.create(order=order, status='cancelled')

    messages.success(request, f'Đã hủy đơn hàng {order_number}.')
    return redirect('orders:detail', order_number=order_number)


@require_POST
def check_payment_status(request):
    """API endpoint để kiểm tra trạng thái thanh toán (polling)"""
    try:
        data = json.loads(request.body)
        payment_method = data.get('payment_method')
        cart_id = data.get('cart_id')

        # Placeholder logic - trong thực tế sẽ kiểm tra với payment gateway
        # Hiện tại trả về pending để simulate chờ thanh toán

        # Có thể check trong database xem payment đã được xác nhận chưa
        # Ví dụ: Check với MoMo API, VNPay API, etc.

        return JsonResponse({
            'status': 'pending',
            'message': 'Đang chờ thanh toán...'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request'
        }, status=400)


@login_required
@require_POST
def rebuy_order(request, order_number):
    """Mua lại tất cả sản phẩm trong đơn hàng"""
    order = get_object_or_404(
        Order,
        order_number=order_number,
        user=request.user
    )

    # Chỉ cho phép mua lại với đơn hàng đã hoàn thành hoặc đã giao
    if order.status not in ['completed', 'delivered']:
        messages.error(request, 'Chỉ có thể mua lại với đơn hàng đã hoàn thành.')
        return redirect('orders:detail', order_number=order_number)

    cart = get_or_create_cart(request)
    added_count = 0
    out_of_stock = []

    for item in order.items.all():
        if item.product and item.product.is_active:
            if item.product.stock > 0:
                # Thêm vào giỏ hàng
                from apps.cart.models import CartItem
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=item.product,
                    defaults={'quantity': item.quantity}
                )
                if not created:
                    # Nếu đã có trong giỏ, tăng số lượng
                    cart_item.quantity += item.quantity
                    # Không vượt quá tồn kho
                    if cart_item.quantity > item.product.stock:
                        cart_item.quantity = item.product.stock
                    cart_item.save()
                added_count += 1
            else:
                out_of_stock.append(item.product_name)
        else:
            out_of_stock.append(item.product_name)

    if added_count > 0:
        messages.success(request, f'Đã thêm {added_count} sản phẩm vào giỏ hàng.')

    if out_of_stock:
        messages.warning(request,
                         f'Một số sản phẩm đã hết hàng: {", ".join(out_of_stock[:3])}{"..." if len(out_of_stock) > 3 else ""}')

    return redirect('cart:detail')


@login_required
@require_POST
def rebuy_item(request, order_number, item_id):
    """Mua lại một sản phẩm cụ thể trong đơn hàng"""
    order = get_object_or_404(
        Order,
        order_number=order_number,
        user=request.user
    )

    item = get_object_or_404(OrderItem, pk=item_id, order=order)

    if not item.product or not item.product.is_active:
        messages.error(request, 'Sản phẩm này không còn khả dụng.')
        return redirect('orders:detail', order_number=order_number)

    if item.product.stock <= 0:
        messages.error(request, f'Sản phẩm "{item.product_name}" đã hết hàng.')
        return redirect('orders:detail', order_number=order_number)

    cart = get_or_create_cart(request)

    from apps.cart.models import CartItem
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=item.product,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        if cart_item.quantity > item.product.stock:
            cart_item.quantity = item.product.stock
        cart_item.save()

    messages.success(request, f'Đã thêm "{item.product_name}" vào giỏ hàng.')
    return redirect('cart:detail')


