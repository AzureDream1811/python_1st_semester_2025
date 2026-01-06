from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Review, ReviewHelpful
from .sentiment import SentimentAnalyzer
from apps.products.models import Product
from apps.orders.models import OrderItem


@login_required
@require_POST
def add_review(request, product_slug):
    """Thêm đánh giá sản phẩm"""
    product = get_object_or_404(Product, slug=product_slug, is_active=True)

    # Kiểm tra user đã mua sản phẩm chưa
    purchased_items = OrderItem.objects.filter(
        order__user=request.user,
        order__status='completed',
        product=product
    )

    # Kiểm tra đã review chưa
    existing_review = Review.objects.filter(
        user=request.user,
        product=product
    ).first()

    if existing_review:
        messages.warning(request, 'Bạn đã đánh giá sản phẩm này rồi.')
        return redirect('products:detail', slug=product_slug)

    # Validate input
    rating = int(request.POST.get('rating', 5))
    comment = request.POST.get('comment', '').strip()

    if not comment:
        messages.error(request, 'Vui lòng nhập nội dung đánh giá.')
        return redirect('products:detail', slug=product_slug)

    if rating < 1 or rating > 5:
        rating = 5

    # Tạo review
    review = Review(
        product=product,
        user=request.user,
        rating=rating,
        comment=comment,
        is_verified_purchase=purchased_items.exists()
    )

    # Link với order item nếu có
    if purchased_items.exists():
        review.order_item = purchased_items.first()

    # Phân tích sentiment
    try:
        analyzer = SentimentAnalyzer()
        result = analyzer.analyze(comment)
        review.sentiment = result['sentiment']
        review.sentiment_score = result['score']
    except Exception as e:
        print(f"⚠️  Lỗi sentiment analysis: {e}")
        review.sentiment = 'neutral'
        review.sentiment_score = 0.0

    # Handle images
    for i in range(1, 4):
        image = request.FILES.get(f'image{i}')
        if image:
            setattr(review, f'image{i}', image)

    review.save()

    # Update product sentiment stats
    try:
        product.update_sentiment_stats()
    except Exception as e:
        print(f"⚠️  Lỗi update sentiment stats: {e}")

    messages.success(request, 'Cảm ơn bạn đã đánh giá sản phẩm!')
    return redirect('products:detail', slug=product_slug)


@login_required
@require_POST
def edit_review(request, review_id):
    """Sửa đánh giá của chính mình"""
    review = get_object_or_404(Review, pk=review_id)
    
    # Kiểm tra quyền
    if review.user != request.user:
        messages.error(request, 'Bạn không có quyền sửa đánh giá này.')
        return redirect('products:detail', slug=review.product.slug)
    
    # Validate input
    rating = int(request.POST.get('rating', review.rating))
    comment = request.POST.get('comment', '').strip()
    
    if not comment:
        messages.error(request, 'Vui lòng nhập nội dung đánh giá.')
        return redirect('products:detail', slug=review.product.slug)
    
    if rating < 1 or rating > 5:
        rating = 5
    
    # Cập nhật review
    review.rating = rating
    review.comment = comment
    
    # Phân tích lại sentiment
    try:
        analyzer = SentimentAnalyzer()
        result = analyzer.analyze(comment)
        review.sentiment = result['sentiment']
        review.sentiment_score = result['score']
    except Exception as e:
        print(f"⚠️  Lỗi sentiment analysis: {e}")
    
    # Handle images nếu có upload mới
    for i in range(1, 4):
        image = request.FILES.get(f'image{i}')
        if image:
            setattr(review, f'image{i}', image)
    
    review.save()
    
    # Update product sentiment stats
    try:
        review.product.update_sentiment_stats()
    except Exception as e:
        print(f"⚠️  Lỗi update sentiment stats: {e}")
    
    messages.success(request, 'Đã cập nhật đánh giá của bạn.')
    return redirect('products:detail', slug=review.product.slug)


@login_required
@require_POST
def delete_review(request, review_id):
    """Xóa đánh giá của chính mình"""
    review = get_object_or_404(Review, pk=review_id)
    
    # Kiểm tra quyền
    if review.user != request.user:
        messages.error(request, 'Bạn không có quyền xóa đánh giá này.')
        return redirect('products:detail', slug=review.product.slug)
    
    product_slug = review.product.slug
    product = review.product
    
    # Xóa review
    review.delete()
    
    # Cập nhật lại sentiment stats cho product
    try:
        product.update_sentiment_stats()
    except Exception as e:
        print(f"⚠️  Lỗi update sentiment stats: {e}")
    
    messages.success(request, 'Đã xóa đánh giá của bạn.')
    return redirect('products:detail', slug=product_slug)


def product_reviews(request, product_slug):
    """Danh sách đánh giá của sản phẩm"""
    product = get_object_or_404(Product, slug=product_slug, is_active=True)

    reviews = Review.objects.filter(
        product=product,
        is_approved=True
    ).select_related('user')

    # Sort
    sort = request.GET.get('sort', '-created_at')
    if sort == 'helpful':
        reviews = reviews.order_by('-helpful_count', '-created_at')
    elif sort == 'rating_high':
        reviews = reviews.order_by('-rating', '-created_at')
    elif sort == 'rating_low':
        reviews = reviews.order_by('rating', '-created_at')
    else:
        reviews = reviews.order_by('-created_at')

    # Pagination
    paginator = Paginator(reviews, 10)
    page = request.GET.get('page', 1)
    reviews = paginator.get_page(page)

    context = {
        'product': product,
        'reviews': reviews,
        'current_sort': sort,
    }
    return render(request, 'reviews/product_reviews.html', context)


@login_required
@require_POST
def mark_helpful(request, review_id):
    """Đánh dấu review hữu ích"""
    review = get_object_or_404(Review, pk=review_id, is_approved=True)

    # Toggle helpful vote
    helpful, created = ReviewHelpful.objects.get_or_create(
        review=review,
        user=request.user
    )

    if not created:
        helpful.delete()
        action = 'removed'
    else:
        action = 'added'

    # Return JSON for AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'action': action,
            'helpful_count': review.helpful_count,
        })

    return redirect('products:detail', slug=review.product.slug)