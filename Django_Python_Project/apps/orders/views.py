import uuid
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction

from .models import Order, OrderItem, OrderHistory
from apps.cart.views import get_or_create_cart
from apps.cart.models import Cart


def generate_order_number():
    """Tạo mã đơn hàng unique"""
    date_str = datetime.now().strftime('%Y%m%d')
    unique_id = uuid.uuid4().hex[:6].upper()
    return f"DH{date_str}{unique_id}"


@login_required
def checkout(request):
    """Trang thanh toán"""
    cart = get_or_create_cart(request)
    items = cart.items.select_related('product').all()

    if not items.exists():
        messages.warning(request, 'Giỏ hàng trống. Vui lòng thêm sản phẩm.')
        return redirect('cart:detail')

    if request.method == 'POST':
        # Validate và tạo đơn hàng
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        district = request.POST.get('district', '').strip()
        city = request.POST.get('city', '').strip()
        ward = request.POST.get('ward', '').strip()
        note = request.POST.get('note', '').strip()
        payment_method = request.POST.get('payment_method', 'cod')

        # Basic validation
        if not all([full_name, email, phone, address, district, city]):
            messages.error(request, 'Vui lòng điền đầy đủ thông tin giao hàng.')
            return render(request, 'orders/checkout.html', {
                'cart': cart,
                'items': items,
            })

        with transaction.atomic():
            # Tạo Order
            order = Order.objects.create(
                order_number=generate_order_number(),
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
                    product_image=item.product.image.url if item.product.image else '',
                    price=item.price,
                    quantity=item.quantity,
                )

                # Giảm stock
                item.product.stock -= item.quantity
                item.product.sold += item.quantity
                item.product.save(update_fields=['stock', 'sold'])

            # Tạo order history
            OrderHistory.objects.create(order=order, status='pending')

            # Clear cart
            cart.clear()

        messages.success(request, f'Đặt hàng thành công! Mã đơn hàng: {order.order_number}')
        return redirect('orders:detail', order_number=order.order_number)

    # Pre-fill từ profile
    profile = getattr(request.user, 'profile', None)

    context = {
        'cart': cart,
        'items': items,
        'profile': profile,
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
