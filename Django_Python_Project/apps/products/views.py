from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, F, Avg
from django.http import JsonResponse

from .models import Product, Category, Brand


def _get_flash_sale_product_ids():
    """Lấy danh sách ID sản phẩm đang trong Flash Sale"""
    from django.utils import timezone
    try:
        from apps.promotions.models import FlashSale
        now = timezone.now()
        return list(FlashSale.objects.filter(
            start_time__lte=now,
            end_time__gte=now,
            is_active=True
        ).values_list('product_id', flat=True))
    except Exception:
        return []


def home(request):
    """Trang chủ - hiển thị sản phẩm nổi bật và mới"""
    from django.utils import timezone

    # Lấy ID sản phẩm flash sale để loại trừ khỏi các phần khác
    flash_sale_ids = _get_flash_sale_product_ids()

    featured_products = Product.objects.filter(
        is_active=True,
        is_featured=True
    ).exclude(id__in=flash_sale_ids).select_related('category', 'brand')[:8]

    new_products = Product.objects.filter(
        is_active=True,
        is_new=True
    ).exclude(id__in=flash_sale_ids).select_related('category', 'brand')[:8]

    categories = Category.objects.filter(is_active=True)[:6]

    # AI Recommended Products - sản phẩm có sentiment tốt
    recommended_products = Product.objects.filter(
        is_active=True,
        sentiment_score__gt=0.3
    ).exclude(id__in=flash_sale_ids).select_related('category', 'brand').order_by('-sentiment_score')[:4]

    # Best sellers - sản phẩm bán chạy nhất
    best_sellers = Product.objects.filter(
        is_active=True
    ).exclude(id__in=flash_sale_ids).select_related('category', 'brand').order_by('-sold')[:8]

    # Flash sale products - sản phẩm đang flash sale
    flash_sale_products = []
    try:
        from apps.promotions.models import FlashSale
        now = timezone.now()
        flash_sale_products = FlashSale.objects.filter(
            start_time__lte=now,
            end_time__gte=now,
            is_active=True
        ).select_related('product', 'product__category', 'product__brand')[:4]
    except Exception:
        pass

    context = {
        'featured_products': featured_products,
        'new_products': new_products,
        'categories': categories,
        'recommended_products': recommended_products,
        'best_sellers': best_sellers,
        'flash_sale_products': flash_sale_products,
    }
    return render(request, 'products/home.html', context)


def product_list(request):
    """Danh sách sản phẩm với filter và pagination"""
    # Loại bỏ sản phẩm flash sale khỏi danh sách thường
    flash_sale_ids = _get_flash_sale_product_ids()
    products = Product.objects.filter(is_active=True).exclude(id__in=flash_sale_ids).select_related('category',
                                                                                                    'brand').annotate(
        avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True))
    )

    # Filter theo multiple categories
    category_slugs = request.GET.getlist('category')
    if category_slugs:
        products = products.filter(category__slug__in=category_slugs)

    # Filter theo multiple brands
    brand_slugs = request.GET.getlist('brand')
    if brand_slugs:
        products = products.filter(brand__slug__in=brand_slugs)

    # Filter theo price range
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Filter theo rating (số sao đánh giá trở lên)
    rating = request.GET.get('rating')
    if rating:
        try:
            rating_value = int(rating)
            if 1 <= rating_value <= 5:
                products = products.filter(avg_rating__gte=rating_value)
        except (ValueError, TypeError):
            pass

    # Sort
    sort = request.GET.get('sort', '-created_at')
    if sort == '-average_rating':
        products = products.order_by(F('avg_rating').desc(nulls_last=True))
    elif sort in ['price', '-price', 'name', '-name', '-created_at', '-sold']:
        products = products.order_by(sort)

    # Pagination
    paginator = Paginator(products, 12)
    page = request.GET.get('page', 1)
    products = paginator.get_page(page)

    # Get categories và brands cho filter sidebar
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)

    # Count discounted products (products with sale_price < price)
    discounted_count = Product.objects.filter(
        is_active=True,
        sale_price__isnull=False,
        sale_price__lt=F('price')
    ).count()

    context = {
        'products': products,
        'categories': categories,
        'brands': brands,
        'discounted_count': discounted_count,
        'selected_categories': category_slugs,
        'selected_brands': brand_slugs,
        'current_sort': sort,
    }
    return render(request, 'products/product_list.html', context)


def product_detail(request, slug):
    """Chi tiết sản phẩm"""
    product = get_object_or_404(
        Product.objects.select_related('category', 'brand'),
        slug=slug,
        is_active=True
    )

    # Tăng view count
    Product.objects.filter(pk=product.pk).update(views=product.views + 1)

    # Load related products
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(pk=product.pk).select_related('category', 'brand')[:4]

    # Load reviews
    reviews = product.reviews.filter(is_approved=True).select_related('user')[:10]

    # Check if product is in user's wishlist
    is_in_wishlist = False
    can_review = False
    has_reviewed = False

    if request.user.is_authenticated:
        is_in_wishlist = Wishlist.objects.filter(
            user=request.user,
            product=product
        ).exists()

        # Kiểm tra đã đánh giá chưa
        from apps.reviews.models import Review
        has_reviewed = Review.objects.filter(
            user=request.user,
            product=product
        ).exists()

        # Kiểm tra có thể đánh giá: đơn hàng hoàn thành + đã thanh toán
        if not has_reviewed:
            from apps.orders.models import OrderItem
            can_review = OrderItem.objects.filter(
                order__user=request.user,
                order__status='completed',
                order__payment_status='paid',
                product=product
            ).exists()

    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'is_in_wishlist': is_in_wishlist,
        'can_review': can_review,
        'has_reviewed': has_reviewed,
    }
    return render(request, 'products/product_detail.html', context)


def category_products(request, slug):
    """Sản phẩm theo danh mục"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    # Loại bỏ sản phẩm flash sale
    flash_sale_ids = _get_flash_sale_product_ids()
    products = Product.objects.filter(
        category=category,
        is_active=True
    ).exclude(id__in=flash_sale_ids).select_related('category', 'brand')

    # Sort
    sort = request.GET.get('sort', '-created_at')
    if sort in ['price', '-price', 'name', '-name', '-created_at', '-sold']:
        products = products.order_by(sort)

    # Pagination
    paginator = Paginator(products, 12)
    page = request.GET.get('page', 1)
    products = paginator.get_page(page)

    context = {
        'category': category,
        'products': products,
        'current_sort': sort,
    }
    return render(request, 'products/category_products.html', context)


# Search đã chuyển sang search app (apps/search/views.py)
# Sử dụng search:search thay vì products:search


# Error Handlers
def error_404(request, exception):
    """Custom 404 error handler"""
    return render(request, '404.html', status=404)


def error_500(request):
    """Custom 500 error handler"""
    return render(request, '500.html', status=500)


def error_403(request, exception):
    """Custom 403 error handler"""
    return render(request, '403.html', status=403)


from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Wishlist


@login_required
def wishlist_view(request):
    """Hiển thị danh sách sản phẩm yêu thích của người dùng"""
    wishlist_items = Wishlist.objects.filter(
        user=request.user
    ).select_related('product', 'product__category', 'product__brand').order_by('-created_at')

    # Pagination
    paginator = Paginator(wishlist_items, 12)
    page = request.GET.get('page', 1)
    wishlist_items = paginator.get_page(page)

    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'products/wishlist.html', context)


@require_POST
def toggle_wishlist(request, product_id):
    """Toggle sản phẩm trong wishlist (thêm/xóa)"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'require_login': True,
            'message': 'Vui lòng đăng nhập để sử dụng tính năng yêu thích'
        }, status=401)

    try:
        product = get_object_or_404(Product, id=product_id, is_active=True)
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )

        if not created:
            wishlist_item.delete()
            return JsonResponse({
                'success': True,
                'action': 'removed',
                'message': f'Đã xóa "{product.name}" khỏi danh sách yêu thích'
            })
        else:
            return JsonResponse({
                'success': True,
                'action': 'added',
                'message': f'Đã thêm "{product.name}" vào danh sách yêu thích'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
@require_POST
def remove_from_wishlist(request, product_id):
    """Xóa sản phẩm khỏi wishlist"""
    try:
        wishlist_item = get_object_or_404(
            Wishlist,
            user=request.user,
            product_id=product_id
        )
        product_name = wishlist_item.product.name
        wishlist_item.delete()

        return JsonResponse({
            'success': True,
            'message': f'Đã xóa "{product_name}" khỏi danh sách yêu thích'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


def get_wishlist_ids(request):
    """API lấy danh sách product IDs trong wishlist của user"""
    if request.user.is_authenticated:
        wishlist_ids = list(
            Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
        )
        return JsonResponse({'wishlist_ids': wishlist_ids})
    return JsonResponse({'wishlist_ids': []})


# ============== SENTIMENT-BASED RECOMMENDATION VIEWS ==============

def recommended_products(request):
    """
    Sản phẩm được gợi ý dựa trên sentiment analysis
    Hiển thị sản phẩm có đánh giá tích cực nhất
    """
    from django.db.models import Count, F

    # Lấy sản phẩm có sentiment tốt (score > 0.3) và có ít nhất 3 reviews
    products = Product.objects.filter(
        is_active=True,
        sentiment_score__gt=0.3
    ).annotate(
        total_reviews=Count('reviews', filter=Q(reviews__is_approved=True))
    ).filter(
        total_reviews__gte=3
    ).select_related('category', 'brand').order_by('-sentiment_score', '-total_reviews')

    # Pagination
    paginator = Paginator(products, 12)
    page = request.GET.get('page', 1)
    products = paginator.get_page(page)

    context = {
        'products': products,
        'page_title': 'Sản phẩm được đánh giá tốt nhất',
        'page_description': 'Những sản phẩm được khách hàng đánh giá tích cực nhất dựa trên phân tích AI',
    }
    return render(request, 'products/recommended_products.html', context)


def top_rated_by_sentiment(request):
    """
    API trả về top sản phẩm theo sentiment cho trang chủ
    """
    products = Product.objects.filter(
        is_active=True,
        sentiment_score__gt=0.3
    ).select_related('category', 'brand').order_by('-sentiment_score')[:8]

    data = [{
        'id': p.id,
        'name': p.name,
        'slug': p.slug,
        'price': float(p.current_price),
        'image': p.image.url if p.image else None,
        'sentiment_score': p.sentiment_score,
        'positive_reviews': p.positive_reviews,
        'negative_reviews': p.negative_reviews,
        'average_rating': p.average_rating,
    } for p in products]

    return JsonResponse({'products': data})


def sentiment_warning(request, product_id):
    """
    API kiểm tra và trả về cảnh báo sentiment cho sản phẩm
    """
    try:
        product = Product.objects.get(id=product_id, is_active=True)

        warning = None
        recommendation = None

        if product.sentiment_score > 0.5 and product.positive_reviews >= 5:
            recommendation = {
                'type': 'positive',
                'title': 'Rất đáng mua!',
                'message': f'Sản phẩm này có {product.positive_reviews} đánh giá tích cực. Khách hàng rất hài lòng với sản phẩm.',
                'icon': 'bi-hand-thumbs-up-fill'
            }
        elif product.sentiment_score > 0.2:
            recommendation = {
                'type': 'good',
                'title': 'Nên mua',
                'message': 'Sản phẩm được đánh giá khá tốt bởi người mua trước.',
                'icon': 'bi-check-circle-fill'
            }
        elif product.sentiment_score < -0.3 and product.negative_reviews >= 3:
            warning = {
                'type': 'negative',
                'title': 'Cân nhắc kỹ!',
                'message': f'Sản phẩm có {product.negative_reviews} đánh giá tiêu cực. Hãy đọc kỹ các đánh giá trước khi mua.',
                'icon': 'bi-exclamation-triangle-fill'
            }
        elif product.sentiment_score < -0.1:
            warning = {
                'type': 'caution',
                'title': 'Lưu ý',
                'message': 'Một số khách hàng không hài lòng với sản phẩm này.',
                'icon': 'bi-info-circle-fill'
            }

        return JsonResponse({
            'success': True,
            'product_id': product_id,
            'sentiment_score': product.sentiment_score,
            'positive_reviews': product.positive_reviews,
            'negative_reviews': product.negative_reviews,
            'warning': warning,
            'recommendation': recommendation
        })
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Sản phẩm không tồn tại'}, status=404)


def products_by_sentiment(request):
    """
    Lọc sản phẩm theo mức độ sentiment
    """
    sentiment_filter = request.GET.get('sentiment', 'all')
    category_slug = request.GET.get('category')

    products = Product.objects.filter(is_active=True).select_related('category', 'brand')

    # Filter theo category
    if category_slug:
        products = products.filter(category__slug=category_slug)

    # Filter theo sentiment
    if sentiment_filter == 'positive':
        products = products.filter(sentiment_score__gt=0.3).order_by('-sentiment_score')
    elif sentiment_filter == 'negative':
        products = products.filter(sentiment_score__lt=-0.3).order_by('sentiment_score')
    elif sentiment_filter == 'neutral':
        products = products.filter(sentiment_score__gte=-0.3, sentiment_score__lte=0.3)
    else:
        products = products.order_by('-sentiment_score')

    # Pagination
    paginator = Paginator(products, 12)
    page = request.GET.get('page', 1)
    products = paginator.get_page(page)

    categories = Category.objects.filter(is_active=True)

    context = {
        'products': products,
        'categories': categories,
        'current_sentiment': sentiment_filter,
        'current_category': category_slug,
    }
    return render(request, 'products/products_by_sentiment.html', context)


def shopping_guide(request):
    """Hướng dẫn mua hàng"""
    return render(request, 'pages/shopping_guide.html')


def return_policy(request):
    """Chính sách đổi trả"""
    return render(request, 'pages/return_policy.html')


def warranty_policy(request):
    """Chính sách bảo hành"""
    return render(request, 'pages/warranty_policy.html')


def faq(request):
    """Câu hỏi thường gặp"""
    return render(request, 'pages/faq.html')
