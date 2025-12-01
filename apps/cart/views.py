from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from apps.products.models import Product
from .models import Cart, CartItem


def get_or_create_cart(request):
    """Lấy hoặc tạo giỏ hàng cho user/session"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Merge session cart nếu có
        session_key = request.session.session_key
        if session_key:
            session_cart = Cart.objects.filter(
                session_key=session_key,
                user__isnull=True
            ).first()
            if session_cart:
                cart.merge_cart(session_cart)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(
            session_key=session_key,
            user__isnull=True
        )
    
    return cart


def cart_view(request):
    """Xem giỏ hàng"""
    cart = get_or_create_cart(request)
    items = cart.items.select_related('product', 'product__brand').all()
    
    context = {
        'cart': cart,
        'items': items,
    }
    return render(request, 'cart/cart.html', context)


@require_POST
def add_to_cart(request, product_id):
    """Thêm sản phẩm vào giỏ"""
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart = get_or_create_cart(request)
    quantity = int(request.POST.get('quantity', 1))
    
    # Kiểm tra tồn kho
    if quantity > product.stock:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': f'Chỉ còn {product.stock} sản phẩm trong kho'
            })
        messages.error(request, f'Chỉ còn {product.stock} sản phẩm trong kho')
        return redirect(request.META.get('HTTP_REFERER', 'products:home'))
    
    # Thêm hoặc cập nhật item
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        new_quantity = cart_item.quantity + quantity
        if new_quantity > product.stock:
            new_quantity = product.stock
        cart_item.quantity = new_quantity
        cart_item.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': 'Đã thêm vào giỏ hàng',
            'cart_total': cart.total_items,
            'cart_subtotal': str(cart.subtotal),
        })
    
    messages.success(request, f'Đã thêm "{product.name}" vào giỏ hàng!')
    return redirect(request.META.get('HTTP_REFERER', 'cart:cart'))


@require_POST
def update_cart(request, item_id):
    """Cập nhật số lượng"""
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity <= 0:
        item.delete()
        message = 'Đã xóa sản phẩm khỏi giỏ hàng'
    elif quantity > item.product.stock:
        item.quantity = item.product.stock
        item.save()
        message = f'Số lượng đã được điều chỉnh về {item.product.stock}'
    else:
        item.quantity = quantity
        item.save()
        message = 'Đã cập nhật số lượng'
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': message,
            'item_total': str(item.total_price) if quantity > 0 else '0',
            'cart_total': cart.total_items,
            'cart_subtotal': str(cart.subtotal),
        })
    
    messages.success(request, message)
    return redirect('cart:cart')


@require_POST
def remove_from_cart(request, item_id):
    """Xóa sản phẩm khỏi giỏ"""
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    
    product_name = item.product.name
    item.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': f'Đã xóa "{product_name}" khỏi giỏ hàng',
            'cart_total': cart.total_items,
            'cart_subtotal': str(cart.subtotal),
        })
    
    messages.success(request, f'Đã xóa "{product_name}" khỏi giỏ hàng!')
    return redirect('cart:cart')


@require_POST
def clear_cart(request):
    """Xóa toàn bộ giỏ hàng"""
    cart = get_or_create_cart(request)
    cart.clear()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': 'Đã xóa toàn bộ giỏ hàng',
        })
    
    messages.success(request, 'Đã xóa toàn bộ giỏ hàng!')
    return redirect('cart:cart')


def cart_count(request):
    """API lấy số lượng item trong giỏ"""
    cart = get_or_create_cart(request)
    return JsonResponse({
        'count': cart.total_items,
        'subtotal': str(cart.subtotal),
    })
