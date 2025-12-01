from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator

from apps.cart.views import get_or_create_cart
from .models import Order, OrderItem, OrderHistory
from .forms import CheckoutForm


def checkout_view(request):
    """Trang thanh toán"""
    cart = get_or_create_cart(request)
    items = cart.items.select_related('product').all()
    
    if not items.exists():
        messages.warning(request, 'Giỏ hàng của bạn đang trống!')
        return redirect('cart:cart')
    
    # Kiểm tra tồn kho
    for item in items:
        if item.quantity > item.product.stock:
            messages.error(
                request,
                f'Sản phẩm "{item.product.name}" chỉ còn {item.product.stock} trong kho'
            )
            return redirect('cart:cart')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST, user=request.user)
        if form.is_valid():
            with transaction.atomic():
                # Tạo đơn hàng
                order = form.save(commit=False)
                if request.user.is_authenticated:
                    order.user = request.user
                order.subtotal = cart.subtotal
                order.shipping_fee = 30000  # Phí ship cố định
                order.total = cart.subtotal + order.shipping_fee
                order.save()
                
                # Tạo order items và cập nhật kho
                for item in items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        product_name=item.product.name,
                        product_sku=item.product.sku,
                        product_image=item.product.image.url if item.product.image else '',
                        price=item.product.current_price,
                        quantity=item.quantity
                    )
                    
                    # Giảm tồn kho và tăng số lượng đã bán
                    item.product.stock -= item.quantity
                    item.product.sold += item.quantity
                    item.product.save(update_fields=['stock', 'sold'])
                
                # Tạo lịch sử đơn hàng
                OrderHistory.objects.create(
                    order=order,
                    status='pending',
                    note='Đơn hàng được tạo',
                    created_by=request.user if request.user.is_authenticated else None
                )
                
                # Xóa giỏ hàng
                cart.clear()
                
                messages.success(request, f'Đặt hàng thành công! Mã đơn hàng: {order.order_number}')
                return redirect('orders:success', order_number=order.order_number)
    else:
        form = CheckoutForm(user=request.user)
    
    # Tính phí ship
    shipping_fee = 30000
    total = cart.subtotal + shipping_fee
    
    context = {
        'form': form,
        'cart': cart,
        'items': items,
        'shipping_fee': shipping_fee,
        'total': total,
    }
    return render(request, 'orders/checkout.html', context)


def order_success_view(request, order_number):
    """Trang đặt hàng thành công"""
    order = get_object_or_404(Order, order_number=order_number)
    
    # Kiểm tra quyền xem
    if request.user.is_authenticated:
        if order.user and order.user != request.user:
            messages.error(request, 'Bạn không có quyền xem đơn hàng này!')
            return redirect('products:home')
    
    return render(request, 'orders/order_success.html', {'order': order})


@login_required
def order_list_view(request):
    """Danh sách đơn hàng của user"""
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    
    # Filter theo trạng thái
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    # Phân trang
    paginator = Paginator(orders, 10)
    page = request.GET.get('page', 1)
    orders = paginator.get_page(page)
    
    context = {
        'orders': orders,
        'current_status': status,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'orders/order_list.html', context)


@login_required
def order_detail_view(request, order_number):
    """Chi tiết đơn hàng"""
    order = get_object_or_404(
        Order.objects.prefetch_related('items', 'history'),
        order_number=order_number,
        user=request.user
    )
    
    context = {
        'order': order,
        'items': order.items.all(),
        'history': order.history.all(),
    }
    return render(request, 'orders/order_detail.html', context)


@login_required
def cancel_order_view(request, order_number):
    """Hủy đơn hàng"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    if not order.can_cancel():
        messages.error(request, 'Không thể hủy đơn hàng này!')
        return redirect('orders:detail', order_number=order_number)
    
    if request.method == 'POST':
        with transaction.atomic():
            # Hoàn lại tồn kho
            for item in order.items.all():
                if item.product:
                    item.product.stock += item.quantity
                    item.product.sold -= item.quantity
                    item.product.save(update_fields=['stock', 'sold'])
            
            # Cập nhật trạng thái
            order.status = 'cancelled'
            order.save(update_fields=['status'])
            
            # Tạo lịch sử
            OrderHistory.objects.create(
                order=order,
                status='cancelled',
                note='Khách hàng hủy đơn hàng',
                created_by=request.user
            )
            
            messages.success(request, 'Đã hủy đơn hàng thành công!')
            return redirect('orders:detail', order_number=order_number)
    
    return render(request, 'orders/cancel_confirm.html', {'order': order})


def track_order_view(request):
    """Tra cứu đơn hàng"""
    order = None
    order_number = request.GET.get('order_number')
    
    if order_number:
        order = Order.objects.filter(order_number=order_number).first()
        if not order:
            messages.error(request, 'Không tìm thấy đơn hàng với mã này!')
    
    context = {
        'order': order,
        'order_number': order_number,
    }
    return render(request, 'orders/track_order.html', context)
