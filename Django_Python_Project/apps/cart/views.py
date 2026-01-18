from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Cart, CartItem
from apps.products.models import Product


def get_or_create_cart(request):
    """Lấy hoặc tạo giỏ hàng cho user/session"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart


def merge_session_cart_with_key(request, old_session_key):
    """
    Gộp giỏ hàng session vào user cart khi login.
    Sử dụng old_session_key được lưu TRƯỚC khi login để tránh mất cart
    do Django session rotation.
    
    Flow:
    1. Lưu session_key cũ trước khi gọi login()
    2. Gọi login() - Django có thể rotate session
    3. Gọi hàm này với old_session_key để merge cart
    4. Xóa cart session cũ sau khi merge
    """
    if not request.user.is_authenticated:
        return

    if not old_session_key:
        return

    try:
        # Tìm cart theo session key CŨ (trước khi login)
        session_cart = Cart.objects.get(session_key=old_session_key, user__isnull=True)

        # Lấy hoặc tạo cart cho user đã login
        user_cart, _ = Cart.objects.get_or_create(user=request.user)

        # Merge items từ session cart vào user cart
        # Hàm merge_cart sẽ:
        # - Cộng dồn quantity nếu sản phẩm đã có trong user cart
        # - Chuyển item sang user cart nếu sản phẩm chưa có
        # - XÓA session cart sau khi merge
        user_cart.merge_cart(session_cart)

    except Cart.DoesNotExist:
        # Không có cart session cũ, không cần làm gì
        pass


def cart_detail(request):
    """Xem giỏ hàng"""
    cart = get_or_create_cart(request)
    active_items = cart.items.filter(saved_for_later=False).select_related('product', 'product__category')
    saved_items = cart.items.filter(saved_for_later=True).select_related('product', 'product__category')

    voucher_error = None
    voucher_success = None

    if request.method == 'POST':
        promo_code = request.POST.get('promo_code', '').strip().upper()

        if promo_code:
            from apps.promotions.models import Voucher, VoucherUsage

            try:
                voucher = Voucher.objects.get(code__iexact=promo_code)

                if not voucher.is_valid():
                    voucher_error = 'Mã giảm giá đã hết hạn hoặc không còn hiệu lực.'
                elif cart.subtotal < voucher.min_order_value:
                    voucher_error = f'Đơn hàng tối thiểu {voucher.min_order_value:,.0f}đ để sử dụng mã này.'
                elif request.user.is_authenticated and voucher.usage_limit_per_user > 0:
                    user_usage = VoucherUsage.objects.filter(voucher=voucher, user=request.user).count()
                    if user_usage >= voucher.usage_limit_per_user:
                        voucher_error = 'Bạn đã sử dụng hết số lần cho phép với mã này.'
                    else:
                        cart.apply_voucher(voucher)
                        voucher_success = f'Áp dụng mã "{voucher.code}" thành công! Giảm {cart.discount:,.0f}đ'
                else:
                    cart.apply_voucher(voucher)
                    voucher_success = f'Áp dụng mã "{voucher.code}" thành công! Giảm {cart.discount:,.0f}đ'

            except Voucher.DoesNotExist:
                voucher_error = 'Mã giảm giá không tồn tại.'

    context = {
        'cart': cart,
        'items': active_items,
        'saved_items': saved_items,
        'voucher_error': voucher_error,
        'voucher_success': voucher_success,
    }
    return render(request, 'cart/cart.html', context)


@require_POST
def remove_voucher(request):
    """Xóa voucher khỏi giỏ hàng"""
    cart = get_or_create_cart(request)
    cart.remove_voucher()
    messages.info(request, 'Đã xóa mã giảm giá.')
    return redirect('cart:detail')


@require_POST
def add_to_cart(request, product_id):
    """Thêm sản phẩm vào giỏ hàng"""
    import json

    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart = get_or_create_cart(request)

    # Support both JSON body and form data
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            quantity = int(data.get('quantity', 1))
        except (json.JSONDecodeError, ValueError):
            quantity = 1
    else:
        quantity = int(request.POST.get('quantity', 1))

    # Check for AJAX request (multiple ways)
    is_ajax = (
            request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
            request.content_type == 'application/json' or
            request.headers.get('Accept', '').find('application/json') != -1
    )

    if quantity <= 0:
        quantity = 1

    # Create or update cart item - không giới hạn bởi tồn kho
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        cart_item.quantity = cart_item.quantity + quantity
        cart_item.save()

    if not is_ajax:
        messages.success(request, f'Đã thêm "{product.name}" vào giỏ hàng.')

    # Return JSON for AJAX requests
    if is_ajax:
        return JsonResponse({
            'success': True,
            'cart_count': cart.total_items,
            'message': f'Đã thêm "{product.name}" vào giỏ hàng.'
        })

    return redirect('cart:detail')


@require_POST
def update_cart(request, item_id):
    """Cập nhật số lượng sản phẩm trong giỏ - không giới hạn bởi tồn kho"""
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, pk=item_id, cart=cart)

    quantity = int(request.POST.get('quantity', 1))

    if quantity <= 0:
        cart_item.delete()
        messages.info(request, 'Đã xóa sản phẩm khỏi giỏ hàng.')
    else:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, 'Đã cập nhật giỏ hàng.')

    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': cart.total_items,
            'cart_total': float(cart.total),
            'item_total': float(cart_item.total_price) if quantity > 0 else 0,
        })

    return redirect('cart:detail')


@require_POST
def remove_from_cart(request, item_id):
    """Xóa sản phẩm khỏi giỏ hàng"""
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, pk=item_id, cart=cart)

    product_name = cart_item.product.name
    cart_item.delete()

    messages.info(request, f'Đã xóa "{product_name}" khỏi giỏ hàng.')

    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': cart.total_items,
            'cart_total': float(cart.total),
        })

    return redirect('cart:detail')


@require_POST
def toggle_save_for_later(request, item_id):
    """Toggle trạng thái thanh toán sau của sản phẩm"""
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, pk=item_id, cart=cart)

    cart_item.saved_for_later = not cart_item.saved_for_later
    cart_item.save()

    if cart_item.saved_for_later:
        messages.info(request, f'Đã chuyển "{cart_item.product.name}" sang thanh toán sau.')
    else:
        messages.success(request, f'Đã chuyển "{cart_item.product.name}" vào giỏ hàng.')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'saved_for_later': cart_item.saved_for_later,
            'cart_count': cart.total_items,
            'cart_total': float(cart.total),
        })

    return redirect('cart:detail')


@require_POST
def move_to_cart(request, item_id):
    """Chuyển sản phẩm từ thanh toán sau về giỏ hàng"""
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, pk=item_id, cart=cart)

    cart_item.saved_for_later = False
    cart_item.save()

    messages.success(request, f'Đã chuyển "{cart_item.product.name}" vào giỏ hàng.')

    return redirect('cart:detail')


@require_POST
def add_to_wishlist_from_cart(request, item_id):
    """Thêm sản phẩm vào wishlist từ giỏ hàng"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'require_login': True,
            'message': 'Vui lòng đăng nhập để sử dụng tính năng yêu thích'
        }, status=401)

    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, pk=item_id, cart=cart)

    from apps.products.models import Wishlist
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=cart_item.product
    )

    if created:
        messages.success(request, f'Đã thêm "{cart_item.product.name}" vào danh sách yêu thích.')
    else:
        messages.info(request, f'"{cart_item.product.name}" đã có trong danh sách yêu thích.')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'created': created,
            'message': f'Đã thêm "{cart_item.product.name}" vào danh sách yêu thích.' if created else f'"{cart_item.product.name}" đã có trong danh sách yêu thích.'
        })

    return redirect('cart:detail')
