from .models import Cart


def cart_context(request):
    """Context processor để hiển thị cart count trên header"""
    cart_items_count = 0

    try:
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            session_key = request.session.session_key
            if session_key:
                cart = Cart.objects.filter(session_key=session_key).first()
            else:
                cart = None

        if cart:
            cart_items_count = cart.total_items
    except:
        pass

    return {
        'cart_items_count': cart_items_count,
    }
