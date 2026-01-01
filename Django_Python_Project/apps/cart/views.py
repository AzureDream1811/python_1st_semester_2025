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
    items = cart.items.select_related('product', 'product__category').all()

    context = {
        'cart': cart,
        'items': items,
    }
    return render(request, 'cart/cart.html', context)


@require_POST
def add_to_cart(request, product_id):
    """Thêm sản phẩm vào giỏ hàng"""
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart = get_or_create_cart(request)

    quantity = int(request.POST.get('quantity', 1))

    # Validate stock
    if quantity > product.stock:
        quantity = product.stock
        messages.warning(request, f'Chỉ còn {product.stock} sản phẩm trong kho.')

    if quantity <= 0:
        messages.error(request, 'Sản phẩm đã hết hàng.')
        return redirect('products:detail', slug=product.slug)

    # Create or update cart item
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        new_quantity = cart_item.quantity + quantity
        if new_quantity > product.stock:
            new_quantity = product.stock
            messages.warning(request, f'Đã đạt số lượng tối đa ({product.stock}) trong kho.')
        cart_item.quantity = new_quantity
        cart_item.save()

    messages.success(request, f'Đã thêm "{product.name}" vào giỏ hàng.')

    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': cart.total_items,
            'message': f'Đã thêm "{product.name}" vào giỏ hàng.'
        })

    return redirect('cart:detail')


@require_POST
def update_cart(request, item_id):
    """Cập nhật số lượng sản phẩm trong giỏ"""
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, pk=item_id, cart=cart)

    quantity = int(request.POST.get('quantity', 1))

    if quantity <= 0:
        cart_item.delete()
        messages.info(request, 'Đã xóa sản phẩm khỏi giỏ hàng.')
    else:
        # Validate stock
        if quantity > cart_item.product.stock:
            quantity = cart_item.product.stock
            messages.warning(request, f'Chỉ còn {cart_item.product.stock} sản phẩm trong kho.')

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
