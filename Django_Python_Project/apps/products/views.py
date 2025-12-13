from django.shortcuts import render

def home(request):
    """Trang chủ - hiển thị danh sách sản phẩm"""
    from .models import Product, Category

    products = Product.objects.filter(is_active=True)[:8]
    categories = Category.objects.filter(is_active=True, parent_id=None)

    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'home.html', context)
