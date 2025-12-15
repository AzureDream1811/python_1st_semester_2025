from .models import Cart

def cart_context(request):
    count = 0
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            if request.session.session_key:
                cart = Cart.objects.filter(session_key=request.session.session_key).first()
            else:
                cart = None

        if cart:
            count = cart.total_items
    except Exception:
        pass

    return {'cart_context': count}
