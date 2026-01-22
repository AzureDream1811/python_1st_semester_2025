from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import Review, ReviewHelpful
from .sentiment import SentimentAnalyzer
from apps.products.models import Product
from apps.orders.models import OrderItem


@login_required
@require_POST
def add_review(request, product_slug):
    """Thêm đánh giá sản phẩm - chỉ cho phép khi đã mua và thanh toán"""
    product = get_object_or_404(Product, slug=product_slug, is_active=True)

    # Kiểm tra user đã mua sản phẩm VÀ đã thanh toán chưa
    purchased_items = OrderItem.objects.filter(
        order__user=request.user,
        order__status='completed',
        order__payment_status='paid',
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

    # Kiểm tra điều kiện: phải mua và thanh toán mới được đánh giá
    if not purchased_items.exists():
        messages.error(request, 'Bạn cần mua và thanh toán sản phẩm này trước khi đánh giá.')
        return redirect('products:detail', slug=product_slug)

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

    # Phân tích sentiment với cả text và rating
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze(comment, rating=rating)
    review.sentiment = result['sentiment']
    review.sentiment_score = result['score']

    # Handle images
    for i, field in enumerate(['image1', 'image2', 'image3'], 1):
        image = request.FILES.get(f'image{i}')
        if image:
            setattr(review, field, image)

    review.save()

    # Update product sentiment stats
    product.update_sentiment_stats()

    messages.success(request, 'Cảm ơn bạn đã đánh giá sản phẩm!')
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


@login_required
@require_POST
def edit_review(request, review_id):
    """Chỉnh sửa đánh giá - chỉ cho phép chủ sở hữu"""
    review = get_object_or_404(Review, pk=review_id)

    # Chỉ cho phép chủ sở hữu chỉnh sửa
    if review.user != request.user:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Không có quyền chỉnh sửa'}, status=403)
        messages.error(request, 'Bạn không có quyền chỉnh sửa đánh giá này.')
        return redirect('products:detail', slug=review.product.slug)

    # Lấy dữ liệu từ form
    rating = request.POST.get('rating')
    comment = request.POST.get('comment', '').strip()

    if not comment:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Vui lòng nhập nội dung đánh giá'}, status=400)
        messages.error(request, 'Vui lòng nhập nội dung đánh giá.')
        return redirect('products:detail', slug=review.product.slug)

    if rating:
        rating = int(rating)
        if rating < 1 or rating > 5:
            rating = review.rating
        review.rating = rating

    review.comment = comment

    # Phân tích lại sentiment
    review.analyze_sentiment()
    review.save()

    # Cập nhật stats của product
    review.product.update_sentiment_stats()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Đã cập nhật đánh giá',
            'rating': review.rating,
            'comment': review.comment,
            'sentiment': review.sentiment,
        })

    messages.success(request, 'Đã cập nhật đánh giá của bạn!')
    return redirect('products:detail', slug=review.product.slug)


@login_required
def get_review(request, review_id):
    """API lấy thông tin review để edit"""
    review = get_object_or_404(Review, pk=review_id)

    # Chỉ cho phép chủ sở hữu
    if review.user != request.user:
        return JsonResponse({'success': False, 'error': 'Không có quyền'}, status=403)

    return JsonResponse({
        'success': True,
        'review': {
            'id': review.id,
            'rating': review.rating,
            'comment': review.comment,
        }
    })


@csrf_exempt
@require_POST
def analyze_sentiment_api(request):
    """
    API endpoint để phân tích sentiment của text.
    Sử dụng AI FastText model để phân tích.

    POST /reviews/api/analyze-sentiment/
    Body: { "text": "...", "rating": 5 }

    Returns:
        {
            "success": true,
            "sentiment": "positive|negative|neutral",
            "score": 0.85,
            "text_score": 0.75,
            "rating_score": 1.0,
            "label": "1|0|unknown"
        }
    """
    import json

    try:
        # Parse JSON body
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST

        text = data.get('text', '').strip()
        rating = data.get('rating')

        if rating:
            try:
                rating = int(rating)
                if rating < 1 or rating > 5:
                    rating = None
            except (ValueError, TypeError):
                rating = None

        if not text:
            return JsonResponse({
                'success': False,
                'error': 'Vui lòng nhập nội dung để phân tích'
            }, status=400)

        # Phân tích sentiment
        analyzer = SentimentAnalyzer()
        result = analyzer.analyze(text, rating=rating)

        return JsonResponse({
            'success': True,
            'sentiment': result['sentiment'],
            'score': result['score'],
            'text_score': result['text_score'],
            'rating_score': result['rating_score'],
            'label': result['label'],
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def sentiment_demo(request):
    """Trang demo phân tích sentiment với AI"""
    return render(request, 'reviews/sentiment_demo.html')
