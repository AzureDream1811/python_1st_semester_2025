from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Count, Avg

from apps.products.models import Product
from apps.orders.models import OrderItem
from .models import Review, ReviewHelpful
from .forms import ReviewForm
from .sentiment import analyze_sentiment


@login_required
def create_review_view(request, product_slug, order_item_id=None):
    """Tạo đánh giá sản phẩm"""
    product = get_object_or_404(Product, slug=product_slug, is_active=True)
    order_item = None
    
    # Kiểm tra order_item nếu có
    if order_item_id:
        order_item = get_object_or_404(
            OrderItem,
            pk=order_item_id,
            order__user=request.user,
            product=product
        )
        
        # Kiểm tra đã review chưa
        if hasattr(order_item, 'review'):
            messages.warning(request, 'Bạn đã đánh giá sản phẩm này rồi!')
            return redirect('products:detail', slug=product_slug)
    else:
        # Kiểm tra đã review chưa (không qua order)
        existing_review = Review.objects.filter(
            product=product,
            user=request.user,
            order_item__isnull=True
        ).exists()
        
        if existing_review:
            messages.warning(request, 'Bạn đã đánh giá sản phẩm này rồi!')
            return redirect('products:detail', slug=product_slug)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.order_item = order_item
            review.save()
            
            # Đánh dấu order_item đã review
            if order_item:
                order_item.is_reviewed = True
                order_item.save(update_fields=['is_reviewed'])
            
            messages.success(request, 'Cảm ơn bạn đã đánh giá sản phẩm!')
            return redirect('products:detail', slug=product_slug)
    else:
        form = ReviewForm()
    
    context = {
        'form': form,
        'product': product,
        'order_item': order_item,
    }
    return render(request, 'reviews/create_review.html', context)


def product_reviews_view(request, product_slug):
    """Xem tất cả reviews của sản phẩm"""
    product = get_object_or_404(Product, slug=product_slug, is_active=True)
    reviews = product.reviews.filter(is_approved=True).select_related('user')
    
    # Filter theo rating
    rating = request.GET.get('rating')
    if rating:
        reviews = reviews.filter(rating=rating)
    
    # Filter theo sentiment
    sentiment = request.GET.get('sentiment')
    if sentiment:
        reviews = reviews.filter(sentiment=sentiment)
    
    # Sắp xếp
    sort = request.GET.get('sort', '-created_at')
    sort_options = {
        'newest': '-created_at',
        'oldest': 'created_at',
        'highest': '-rating',
        'lowest': 'rating',
        'helpful': '-helpful_count',
    }
    order_by = sort_options.get(sort, '-created_at')
    reviews = reviews.order_by(order_by)
    
    # Phân trang
    paginator = Paginator(reviews, 10)
    page = request.GET.get('page', 1)
    reviews = paginator.get_page(page)
    
    # Thống kê
    all_reviews = product.reviews.filter(is_approved=True)
    stats = {
        'total': all_reviews.count(),
        'average': all_reviews.aggregate(Avg('rating'))['rating__avg'] or 0,
        'rating_distribution': {},
        'sentiment_distribution': {
            'positive': all_reviews.filter(sentiment='positive').count(),
            'negative': all_reviews.filter(sentiment='negative').count(),
            'neutral': all_reviews.filter(sentiment='neutral').count(),
        }
    }
    
    # Phân bố rating
    for i in range(1, 6):
        count = all_reviews.filter(rating=i).count()
        percent = (count / stats['total'] * 100) if stats['total'] > 0 else 0
        stats['rating_distribution'][i] = {
            'count': count,
            'percent': percent
        }
    
    context = {
        'product': product,
        'reviews': reviews,
        'stats': stats,
        'current_rating': rating,
        'current_sentiment': sentiment,
        'current_sort': sort,
    }
    return render(request, 'reviews/product_reviews.html', context)


@login_required
def my_reviews_view(request):
    """Xem các reviews của user"""
    reviews = Review.objects.filter(user=request.user).select_related('product')
    
    # Phân trang
    paginator = Paginator(reviews, 10)
    page = request.GET.get('page', 1)
    reviews = paginator.get_page(page)
    
    return render(request, 'reviews/my_reviews.html', {'reviews': reviews})


@login_required
def edit_review_view(request, review_id):
    """Chỉnh sửa review"""
    review = get_object_or_404(Review, pk=review_id, user=request.user)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            review = form.save(commit=False)
            # Re-analyze sentiment
            review.sentiment = ''  # Reset để trigger analyze lại
            review.save()
            
            messages.success(request, 'Đã cập nhật đánh giá!')
            return redirect('products:detail', slug=review.product.slug)
    else:
        form = ReviewForm(instance=review)
    
    context = {
        'form': form,
        'review': review,
        'product': review.product,
    }
    return render(request, 'reviews/edit_review.html', context)


@login_required
@require_POST
def delete_review_view(request, review_id):
    """Xóa review"""
    review = get_object_or_404(Review, pk=review_id, user=request.user)
    product_slug = review.product.slug
    
    # Cập nhật order_item
    if review.order_item:
        review.order_item.is_reviewed = False
        review.order_item.save(update_fields=['is_reviewed'])
    
    review.delete()
    
    messages.success(request, 'Đã xóa đánh giá!')
    return redirect('products:detail', slug=product_slug)


@login_required
@require_POST
def mark_helpful_view(request, review_id):
    """Đánh dấu review hữu ích"""
    review = get_object_or_404(Review, pk=review_id, is_approved=True)
    
    # Không thể vote cho review của chính mình
    if review.user == request.user:
        return JsonResponse({
            'status': 'error',
            'message': 'Bạn không thể vote cho đánh giá của chính mình'
        })
    
    # Toggle vote
    helpful, created = ReviewHelpful.objects.get_or_create(
        review=review,
        user=request.user
    )
    
    if not created:
        helpful.delete()
        message = 'Đã bỏ đánh dấu hữu ích'
        is_helpful = False
    else:
        message = 'Đã đánh dấu hữu ích'
        is_helpful = True
    
    return JsonResponse({
        'status': 'success',
        'message': message,
        'is_helpful': is_helpful,
        'helpful_count': review.helpful_count
    })


def analyze_sentiment_api(request):
    """API để test sentiment analysis"""
    text = request.GET.get('text', '')
    
    if not text:
        return JsonResponse({
            'status': 'error',
            'message': 'Vui lòng nhập text để phân tích'
        })
    
    result = analyze_sentiment(text)
    
    return JsonResponse({
        'status': 'success',
        'result': result
    })


@login_required
def pending_reviews_view(request):
    """Xem sản phẩm đã mua chưa review"""
    # Lấy các order items đã giao hàng và chưa review
    pending_items = OrderItem.objects.filter(
        order__user=request.user,
        order__status__in=['delivered', 'completed'],
        is_reviewed=False
    ).select_related('product', 'order')
    
    return render(request, 'reviews/pending_reviews.html', {'pending_items': pending_items})
