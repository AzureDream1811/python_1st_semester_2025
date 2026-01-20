"""
Views Gợi Ý Sản Phẩm cho ElectroShop
"""
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
import json

from apps.products.models import Product
from apps.orders.models import OrderItem
from .models import UserActivity, ProductSimilarity, FrequentlyBoughtTogether


def get_smart_image_url(image_field):
    """Lấy URL đúng cho image field (hỗ trợ cả URL ngoại và local)."""
    if not image_field:
        return None
    image_name = str(image_field.name) if hasattr(image_field, 'name') else str(image_field)
    if image_name.startswith(('http://', 'https://')):
        return image_name
    try:
        return image_field.url
    except (ValueError, AttributeError):
        return None


# =============================================================================
# GỢI Ý CÁ NHÂN HÓA
# =============================================================================

def get_recommendations_for_user(request, user_id=None):
    """
    API trả về gợi ý sản phẩm cá nhân hóa cho user
    
    Thuật toán:
    1. Nếu user đã đăng nhập và có lịch sử mua hàng:
       - Lấy danh sách sản phẩm đã mua
       - Tìm sản phẩm tương tự với những sản phẩm đã mua
       - Loại bỏ sản phẩm đã mua
    2. Nếu không có lịch sử:
       - Trả về sản phẩm phổ biến (bán chạy + đánh giá tốt)
    
    Args:
        user_id: ID của user (optional)
        
    Returns:
        JSON với danh sách sản phẩm gợi ý
    """
    # Xác định user
    if user_id:
        user = request.user if request.user.is_authenticated and request.user.id == user_id else None
    else:
        user = request.user if request.user.is_authenticated else None

    recommendations = []

    if user:
        # Lấy danh sách sản phẩm đã mua
        purchased_products = OrderItem.objects.filter(
            order__user=user,
            order__status='completed'
        ).values_list('product_id', flat=True)

        # Tìm sản phẩm tương tự với những sản phẩm đã mua
        similar_products = ProductSimilarity.objects.filter(
            product_id__in=purchased_products
        ).exclude(
            similar_product_id__in=purchased_products  # Loại bỏ sản phẩm đã mua
        ).select_related('similar_product').order_by('-score')[:10]

        # Chuyển đổi thành response format
        for similarity in similar_products:
            product = similarity.similar_product
            if product.is_active:
                recommendations.append({
                    'id': product.id,
                    'name': product.name,
                    'slug': product.slug,
                    'price': float(product.current_price),
                    'image': get_smart_image_url(product.image),
                    'reason': 'Tương tự sản phẩm bạn đã mua',
                    'score': similarity.score
                })

    # Fallback: Nếu không có gợi ý cá nhân, trả về sản phẩm phổ biến
    if not recommendations:
        popular_products = Product.objects.filter(
            is_active=True,
            sentiment_score__gt=0.3  # Chỉ lấy sản phẩm có đánh giá tích cực
        ).order_by('-sold', '-sentiment_score')[:10]

        for product in popular_products:
            recommendations.append({
                'id': product.id,
                'name': product.name,
                'slug': product.slug,
                'price': float(product.current_price),
                'image': get_smart_image_url(product.image),
                'reason': 'Sản phẩm phổ biến',
                'score': 0.8
            })

    return JsonResponse({
        'recommendations': recommendations[:8],  # Giới hạn 8 sản phẩm
        'user_id': user.id if user else None
    })


# =============================================================================
# SẢN PHẨM TƯƠNG TỰ
# =============================================================================

def get_similar_products(request, product_id):
    """
    API trả về sản phẩm tương tự với sản phẩm đang xem
    
    Thuật toán:
    1. Tìm trong bảng ProductSimilarity (đã tính toán trước)
    2. Nếu không có, fallback sang sản phẩm cùng danh mục
    
    Args:
        product_id: ID của sản phẩm đang xem
        
    Returns:
        JSON với danh sách sản phẩm tương tự
    """
    # Kiểm tra sản phẩm tồn tại
    try:
        product = Product.objects.get(id=product_id, is_active=True)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Không tìm thấy sản phẩm'}, status=404)

    # Tìm sản phẩm tương tự từ bảng pre-computed
    similar_products = ProductSimilarity.objects.filter(
        product=product
    ).select_related('similar_product').order_by('-score')[:8]

    recommendations = []
    for similarity in similar_products:
        similar_product = similarity.similar_product
        if similar_product.is_active:
            recommendations.append({
                'id': similar_product.id,
                'name': similar_product.name,
                'slug': similar_product.slug,
                'price': float(similar_product.current_price),
                'image': get_smart_image_url(similar_product.image),
                'similarity_score': similarity.score
            })

    # Fallback: Nếu không có sản phẩm tương tự, lấy cùng danh mục
    if not recommendations and product.category:
        category_products = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(id=product.id).order_by('-sentiment_score')[:8]

        for similar_product in category_products:
            recommendations.append({
                'id': similar_product.id,
                'name': similar_product.name,
                'slug': similar_product.slug,
                'price': float(similar_product.current_price),
                'image': get_smart_image_url(similar_product.image),
                'similarity_score': 0.5  # Score mặc định cho cùng danh mục
            })

    return JsonResponse({
        'product_id': product_id,
        'similar_products': recommendations
    })


# =============================================================================
# SẢN PHẨM THƯỜNG MUA CÙNG
# =============================================================================

def get_frequently_bought_together(request, product_id):
    """
    API trả về sản phẩm thường được mua cùng
    
    Hiển thị:
    - Danh sách sản phẩm hay mua kèm
    - Tổng giá nếu mua combo
    - Số tiền tiết kiệm (giả định 5%)
    
    Args:
        product_id: ID của sản phẩm chính
        
    Returns:
        JSON với danh sách sản phẩm mua kèm và thông tin combo
    """
    # Kiểm tra sản phẩm tồn tại
    try:
        product = Product.objects.get(id=product_id, is_active=True)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Không tìm thấy sản phẩm'}, status=404)

    # Tìm sản phẩm thường mua cùng
    fbt_products = FrequentlyBoughtTogether.objects.filter(
        product=product
    ).select_related('related_product').order_by('-count')[:6]

    recommendations = []
    total_price = float(product.current_price)

    for fbt in fbt_products:
        related_product = fbt.related_product
        if related_product.is_active:
            recommendations.append({
                'id': related_product.id,
                'name': related_product.name,
                'slug': related_product.slug,
                'price': float(related_product.current_price),
                'image': get_smart_image_url(related_product.image),
                'bought_together_count': fbt.count
            })
            total_price += float(related_product.current_price)

    return JsonResponse({
        'product_id': product_id,
        'main_product': {
            'id': product.id,
            'name': product.name,
            'price': float(product.current_price),
            'image': get_smart_image_url(product.image)
        },
        'frequently_bought_together': recommendations,
        'total_price': total_price,
        'savings': total_price * 0.05  # Giảm 5% khi mua combo
    })


# =============================================================================
# GHI NHẬN HOẠT ĐỘNG NGƯỜI DÙNG
# =============================================================================

@login_required
def log_user_activity(request):
    """
    API ghi nhận hoạt động người dùng
    
    Được gọi từ frontend khi user:
    - Xem sản phẩm
    - Thêm vào giỏ hàng
    - Thêm vào wishlist
    - Tìm kiếm
    
    Method: POST
    
    Request Body:
        - activity_type: Loại hoạt động (view, add_to_cart, wishlist, search)
        - product_id: ID sản phẩm (optional)
        - search_query: Từ khóa tìm kiếm (optional)
        
    Returns:
        JSON với kết quả ghi nhận
    """
    # Chỉ chấp nhận POST
    if request.method != 'POST':
        return JsonResponse({'error': 'Phương thức không được hỗ trợ'}, status=405)

    # Parse JSON body
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Dữ liệu JSON không hợp lệ'}, status=400)

    # Lấy dữ liệu từ request
    activity_type = data.get('activity_type')
    product_id = data.get('product_id')
    search_query = data.get('search_query', '')
    session_id = request.session.session_key or ''

    # Validate activity_type
    if not activity_type:
        return JsonResponse({'error': 'Thiếu activity_type'}, status=400)

    # Chuẩn bị dữ liệu activity
    activity_data = {
        'user': request.user,
        'session_id': session_id,
        'activity_type': activity_type,
        'search_query': search_query,
    }

    # Thêm product nếu có
    if product_id:
        try:
            product = Product.objects.get(id=product_id)
            activity_data['product'] = product
        except Product.DoesNotExist:
            pass  # Bỏ qua nếu product không tồn tại

    # Tạo bản ghi activity
    UserActivity.objects.create(**activity_data)

    return JsonResponse({'success': True})


# =============================================================================
# SẢN PHẨM TRENDING
# =============================================================================

def trending_products(request):
    """
    API trả về sản phẩm đang trending
    
    Thuật toán:
    - Đếm số hoạt động (view, add_to_cart, purchase) trong 7 ngày gần nhất
    - Sắp xếp theo số hoạt động giảm dần
    
    Returns:
        JSON với danh sách sản phẩm trending
    """
    # Lấy hoạt động trong 7 ngày gần nhất
    last_week = timezone.now() - timedelta(days=7)

    # Đếm hoạt động theo sản phẩm
    trending = UserActivity.objects.filter(
        created_at__gte=last_week,
        activity_type__in=['view', 'add_to_cart', 'purchase'],
        product__isnull=False
    ).values('product_id').annotate(
        activity_count=Count('id')
    ).order_by('-activity_count')[:12]

    # Lấy danh sách product_id
    product_ids = [item['product_id'] for item in trending]

    # Query products
    products = Product.objects.filter(
        id__in=product_ids,
        is_active=True
    ).select_related('category', 'brand')

    # Sắp xếp theo thứ tự trending
    products_dict = {p.id: p for p in products}
    sorted_products = [products_dict[pid] for pid in product_ids if pid in products_dict]

    # Chuyển đổi thành response format
    recommendations = []
    for product in sorted_products:
        recommendations.append({
            'id': product.id,
            'name': product.name,
            'slug': product.slug,
            'price': float(product.current_price),
            'image': get_smart_image_url(product.image),
            'category': product.category.name if product.category else None,
            'sentiment_score': product.sentiment_score
        })

    return JsonResponse({
        'trending_products': recommendations
    })
