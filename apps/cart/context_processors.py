from .models import Cart


def cart_context(request):
    """Context processor để hiển thị thông tin giỏ hàng ở mọi trang"""
    cart = None
    cart_items_count = 0
    
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    elif request.session.session_key:
        cart = Cart.objects.filter(
            session_key=request.session.session_key,
            user__isnull=True
        ).first()
    
    if cart:
        cart_items_count = cart.total_items
    
    return {
        'cart': cart,
        'cart_items_count': cart_items_count,
    }
