from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Product, Category, Brand, Wishlist


def home_view(request):
    """Trang chủ"""
    # Sản phẩm nổi bật
    featured_products = Product.objects.filter(
        is_active=True,
        is_featured=True
    ).select_related('category', 'brand')[:8]
    
    # Sản phẩm mới
    new_products = Product.objects.filter(
        is_active=True,
        is_new=True
    ).select_related('category', 'brand')[:8]
    
    # Sản phẩm bán chạy
    best_sellers = Product.objects.filter(
        is_active=True
    ).order_by('-sold').select_related('category', 'brand')[:8]
    
    # Sản phẩm có sentiment tích cực (AI recommended)
    ai_recommended = Product.objects.filter(
        is_active=True,
        sentiment_score__gt=0.3
    ).order_by('-sentiment_score').select_related('category', 'brand')[:8]
    
    # Danh mục chính
    categories = Category.objects.filter(
        is_active=True,
        parent__isnull=True
    )[:6]
    
    # Thương hiệu
    brands = Brand.objects.filter(is_active=True)[:8]
    
    context = {
        'featured_products': featured_products,
        'new_products': new_products,
        'best_sellers': best_sellers,
        'ai_recommended': ai_recommended,
        'categories': categories,
        'brands': brands,
    }
    return render(request, 'products/home.html', context)


def product_list_view(request):
    """Danh sách sản phẩm với filter"""
    products = Product.objects.filter(is_active=True).select_related('category', 'brand')
    
    # Filter theo danh mục
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    # Filter theo thương hiệu
    brand_slug = request.GET.get('brand')
    if brand_slug:
        brand = get_object_or_404(Brand, slug=brand_slug)
        products = products.filter(brand=brand)
    
    # Filter theo giá
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Filter theo sentiment
    sentiment = request.GET.get('sentiment')
    if sentiment == 'positive':
        products = products.filter(sentiment_score__gt=0.3)
    elif sentiment == 'negative':
        products = products.filter(sentiment_score__lt=-0.3)
    
    # Tìm kiếm
    search = request.GET.get('q')
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(brand__name__icontains=search) |
            Q(category__name__icontains=search)
        )
    
    # Sắp xếp
    sort = request.GET.get('sort', '-created_at')
    sort_options = {
        'newest': '-created_at',
        'price_asc': 'price',
        'price_desc': '-price',
        'name': 'name',
        'popular': '-sold',
        'rating': '-sentiment_score',
    }
    order_by = sort_options.get(sort, '-created_at')
    products = products.order_by(order_by)
    
    # Phân trang
    paginator = Paginator(products, 12)
    page = request.GET.get('page', 1)
    products = paginator.get_page(page)
    
    # Danh mục và thương hiệu cho sidebar
    categories = Category.objects.filter(is_active=True, parent__isnull=True)
    brands = Brand.objects.filter(is_active=True)
    
    context = {
        'products': products,
        'categories': categories,
        'brands': brands,
        'current_category': category_slug,
        'current_brand': brand_slug,
        'search_query': search,
        'current_sort': sort,
    }
    return render(request, 'products/product_list.html', context)


def product_detail_view(request, slug):
    """Chi tiết sản phẩm"""
    product = get_object_or_404(
        Product.objects.select_related('category', 'brand'),
        slug=slug,
        is_active=True
    )
    
    # Tăng lượt xem
    product.views += 1
    product.save(update_fields=['views'])
    
    # Sản phẩm liên quan
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(pk=product.pk)[:4]
    
    # Reviews
    reviews = product.reviews.filter(is_approved=True).select_related('user').order_by('-created_at')[:10]
    
    # Kiểm tra wishlist
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()
    
    # Thống kê sentiment
    sentiment_stats = {
        'positive': product.positive_reviews,
        'negative': product.negative_reviews,
        'total': product.positive_reviews + product.negative_reviews,
        'score': product.sentiment_score,
        'label': product.sentiment_label,
    }
    
    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'in_wishlist': in_wishlist,
        'sentiment_stats': sentiment_stats,
    }
    return render(request, 'products/product_detail.html', context)


def category_view(request, slug):
    """Sản phẩm theo danh mục"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    
    # Lấy tất cả danh mục con
    categories_ids = [category.id]
    for child in category.children.filter(is_active=True):
        categories_ids.append(child.id)
    
    products = Product.objects.filter(
        category_id__in=categories_ids,
        is_active=True
    ).select_related('brand')
    
    # Sắp xếp
    sort = request.GET.get('sort', '-created_at')
    sort_options = {
        'newest': '-created_at',
        'price_asc': 'price',
        'price_desc': '-price',
        'popular': '-sold',
    }
    order_by = sort_options.get(sort, '-created_at')
    products = products.order_by(order_by)
    
    # Phân trang
    paginator = Paginator(products, 12)
    page = request.GET.get('page', 1)
    products = paginator.get_page(page)
    
    context = {
        'category': category,
        'products': products,
        'current_sort': sort,
    }
    return render(request, 'products/category.html', context)


def search_view(request):
    """Tìm kiếm sản phẩm"""
    query = request.GET.get('q', '')
    products = Product.objects.filter(is_active=True)
    
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__name__icontains=query) |
            Q(category__name__icontains=query)
        ).select_related('category', 'brand')
    
    # Phân trang
    paginator = Paginator(products, 12)
    page = request.GET.get('page', 1)
    products = paginator.get_page(page)
    
    context = {
        'products': products,
        'query': query,
        'result_count': paginator.count,
    }
    return render(request, 'products/search_results.html', context)


# Wishlist Views
@login_required
def wishlist_view(request):
    """Xem danh sách yêu thích"""
    wishlists = Wishlist.objects.filter(
        user=request.user
    ).select_related('product', 'product__category', 'product__brand')
    
    return render(request, 'products/wishlist.html', {'wishlists': wishlists})


@login_required
@require_POST
def add_to_wishlist(request, product_id):
    """Thêm vào wishlist"""
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    
    wishlist, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': 'Đã thêm vào yêu thích' if created else 'Sản phẩm đã có trong danh sách yêu thích',
            'created': created
        })
    
    if created:
        messages.success(request, 'Đã thêm vào danh sách yêu thích!')
    else:
        messages.info(request, 'Sản phẩm đã có trong danh sách yêu thích.')
    
    return redirect(request.META.get('HTTP_REFERER', 'products:home'))


@login_required
@require_POST
def remove_from_wishlist(request, product_id):
    """Xóa khỏi wishlist"""
    product = get_object_or_404(Product, pk=product_id)
    
    deleted, _ = Wishlist.objects.filter(
        user=request.user,
        product=product
    ).delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': 'Đã xóa khỏi yêu thích' if deleted else 'Không tìm thấy sản phẩm',
            'deleted': deleted > 0
        })
    
    if deleted:
        messages.success(request, 'Đã xóa khỏi danh sách yêu thích!')
    
    return redirect(request.META.get('HTTP_REFERER', 'products:wishlist'))


def ajax_search(request):
    """AJAX tìm kiếm gợi ý"""
    query = request.GET.get('q', '')
    
    if len(query) < 2:
        return JsonResponse({'products': []})
    
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(brand__name__icontains=query),
        is_active=True
    ).select_related('brand')[:5]
    
    results = []
    for product in products:
        results.append({
            'id': product.id,
            'name': product.name,
            'price': str(product.current_price),
            'image': product.image.url if product.image else '',
            'url': product.get_absolute_url(),
        })
    
    return JsonResponse({'products': results})
