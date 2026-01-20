"""
Views cho Search App - ElectroShop

Xử lý các request liên quan đến tìm kiếm sản phẩm:
- Tìm kiếm sản phẩm với bộ lọc
- Autocomplete gợi ý tìm kiếm
- Từ khóa tìm kiếm phổ biến
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator
from apps.products.models import Product, Category, Brand
from .services.search_service import SearchService


def get_smart_image_url(image_field):
    """Lấy URL đúng cho image field (hỗ trợ cả URL ngoại và local)."""
    if not image_field:
        return ''
    image_name = str(image_field.name) if hasattr(image_field, 'name') else str(image_field)
    if image_name.startswith(('http://', 'https://')):
        return image_name
    try:
        return image_field.url
    except (ValueError, AttributeError):
        return ''


def search_products(request):
    """
    Tìm kiếm sản phẩm với bộ lọc và phân trang
    
    URL: /search/?q=<query>&category=<slug>&brand=<slug>&min_price=<int>&max_price=<int>&sort=<field>
    
    Query Parameters:
        q: Từ khóa tìm kiếm
        category: Slug danh mục để lọc
        brand: Slug thương hiệu để lọc
        min_price: Giá tối thiểu
        max_price: Giá tối đa
        rating: Đánh giá tối thiểu (1-5)
        in_stock: 'true' để chỉ lấy sản phẩm còn hàng
        sort: Cách sắp xếp (relevance, price, -price, name, -created_at, -sold)
        page: Số trang (mặc định 1)
    
    Returns:
        - HTML template nếu request thường
        - JSON nếu AJAX request
    """
    # Lấy từ khóa tìm kiếm
    query = request.GET.get('q', '').strip()

    # Thu thập các bộ lọc từ query parameters
    filters = {
        'category': request.GET.get('category'),  # Slug danh mục
        'brand': request.GET.get('brand'),  # Slug thương hiệu
        'min_price': request.GET.get('min_price'),  # Giá tối thiểu
        'max_price': request.GET.get('max_price'),  # Giá tối đa
        'rating': request.GET.get('rating'),  # Đánh giá tối thiểu
        'in_stock': request.GET.get('in_stock'),  # Chỉ còn hàng
    }

    # Loại bỏ các filter rỗng
    filters = {k: v for k, v in filters.items() if v}

    # Lấy cách sắp xếp (mặc định: relevance)
    sort = request.GET.get('sort', 'relevance')

    if query:
        # Ghi log tìm kiếm (để phân tích sau)
        SearchService.log_search(
            query=query,
            user=request.user if request.user.is_authenticated else None
        )

        # Tìm kiếm sản phẩm qua SearchService
        results = SearchService.search_products(query, filters, sort)
    else:
        # Không có từ khóa -> hiển thị tất cả sản phẩm với filter
        results = Product.objects.filter(is_active=True)

        # Áp dụng các bộ lọc thủ công
        if filters.get('category'):
            results = results.filter(category__slug=filters['category'])
        if filters.get('brand'):
            results = results.filter(brand__slug=filters['brand'])
        if filters.get('min_price'):
            results = results.filter(price__gte=filters['min_price'])
        if filters.get('max_price'):
            results = results.filter(price__lte=filters['max_price'])
        if filters.get('in_stock') == 'true':
            results = results.filter(stock__gt=0)

    # Phân trang kết quả (20 sản phẩm/trang)
    paginator = Paginator(results, 20)
    page = request.GET.get('page', 1)
    products = paginator.get_page(page)

    # Lấy danh sách danh mục và thương hiệu cho sidebar filter
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)

    # Chuẩn bị context cho template
    context = {
        'query': query,  # Từ khóa đã tìm
        'products': products,  # Kết quả đã phân trang
        'categories': categories,  # Danh sách danh mục
        'brands': brands,  # Danh sách thương hiệu
        'filters': filters,  # Các filter đang áp dụng
        'sort': sort,  # Cách sắp xếp hiện tại
        'total_results': paginator.count,  # Tổng số kết quả
    }

    # Kiểm tra nếu là AJAX request -> trả về JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'results': [
                {
                    'id': p.id,
                    'name': p.name,
                    'price': float(p.price),
                    'image': get_smart_image_url(p.image),
                    'url': p.get_absolute_url(),
                }
                for p in products
            ],
            'total': paginator.count,
            'page': products.number,
            'pages': paginator.num_pages,
        })

    # Trả về HTML template
    return render(request, 'search/search_results.html', context)


def autocomplete(request):
    """
    API: Lấy gợi ý tìm kiếm (autocomplete)
    
    URL: /search/autocomplete/?q=<query>&limit=<int>
    
    Trả về danh sách tên sản phẩm gợi ý dựa trên từ khóa nhập vào.
    Yêu cầu từ khóa có ít nhất 2 ký tự.
    
    Query Parameters:
        q: Từ khóa tìm kiếm (bắt buộc, >= 2 ký tự)
        limit: Số lượng gợi ý tối đa (mặc định 10)
    
    Returns:
        JSON: {'suggestions': ['Sản phẩm 1', 'Sản phẩm 2', ...]}
    """
    query = request.GET.get('q', '').strip()
    limit = int(request.GET.get('limit', 10))

    # Không gợi ý nếu query quá ngắn
    if len(query) < 2:
        return JsonResponse({'suggestions': []})

    # Lấy gợi ý từ SearchService
    suggestions = SearchService.autocomplete(query, limit)
    return JsonResponse({'suggestions': suggestions})


def search_suggestions(request):
    """
    API: Lấy từ khóa tìm kiếm phổ biến
    
    URL: /search/suggestions/
    
    Trả về danh sách các từ khóa được tìm kiếm nhiều nhất.
    Dùng để hiển thị gợi ý trên trang tìm kiếm khi chưa nhập gì.
    
    Returns:
        JSON: {'suggestions': ['điện thoại', 'laptop', ...]}
    """
    suggestions = SearchService.get_popular_searches(limit=10)
    return JsonResponse({'suggestions': suggestions})
