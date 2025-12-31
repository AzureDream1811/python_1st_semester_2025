from decimal import Decimal, InvalidOperation
from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from ..products.models import Product, Category, Brand
from .services.search_service import SearchService

def search_products(request):
    """Tìm kiếm sản phẩm"""
    query = request.GET.get('q', '').strip()
    # Filters
    filters = {
        'category': request.GET.get('category', ''),
        'brand': request.GET.get('brand', ''),
        'min_price': request.GET.get('min_price', ''),
        'max_price': request.GET.get('max_price', ''),
        'in_stock': request.GET.get('in_stock', '')
    }

    # Remove empty filters
    filters = {k: v for k, v in filters.items() if v}

    # Validate price range
    if 'min_price' in filters and 'max_price' in filters:
        try:
            min_val = Decimal(filters['min_price'])
            max_val = Decimal(filters['max_price'])
            if min_val > max_val:
                del filters['min_price']
                del filters['max_price']
        except (ValueError, InvalidOperation):
            filters.pop('min_price', None)
            filters.pop('max_price', None)

    # Search service
    search_service = SearchService()

    # Build base queryset
    queryset = Product.objects.filter(is_active=True)

    # Apply text search if query exists
    if query:
        normalized_query = search_service.normalize_vietnamese(query)
        queryset = queryset.filter(
            Q(name__icontains=query) |
            Q(name__icontains=normalized_query) |
            Q(description__icontains=query) |
            Q(description__icontains=normalized_query)
        )

    # Apply filters
    if 'category' in filters:
        queryset = queryset.filter(category__slug=filters['category'])

    if 'brand' in filters:
        queryset = queryset.filter(brand__slug=filters['brand'])

    if 'min_price' in filters:
        try:
            queryset = queryset.filter(price__gte=Decimal(filters['min_price']))
        except (ValueError, InvalidOperation):
            pass

    if 'max_price' in filters:
        try:
            queryset = queryset.filter(price__lte=Decimal(filters['max_price']))
        except (ValueError, InvalidOperation):
            pass

    if 'in_stock' in filters and filters['in_stock'] == 'true':
        queryset = queryset.filter(stock__gt=0)


    # Log search if query exists
    if query:
        total_results = queryset.count()
        search_service.log_search(
            query,
            total_results,
            request.user if request.user.is_authenticated else None
        )

    # Pagination
    paginator = Paginator(queryset, 20)
    page_number = request.GET.get('page', 1)

    try:
        products = paginator.get_page(page_number)
    except EmptyPage:
        products = paginator.get_page(1)

    # Get filter options
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)

    context = {
        'query': query,
        'products': products,
        'categories': categories,
        'brands': brands,
        'filters': filters,
        'total_results': paginator.count,
    }

    # Handle AJAX requests
    # if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
    #     return JsonResponse({
    #         'results': [
    #             {
    #                 'id': p.id,
    #                 'name': p.name,
    #                 'price': float(p.price),
    #                 'image': p.image.url if p.image else '',
    #                 'url': p.get_absolute_url(),
    #             }
    #             for p in products
    #         ],
    #         'total': paginator.count,
    #         'page': products.number,
    #         'pages': paginator.num_pages,
    #         'filters': filters,
    #     })

    return render(request, 'search/search_results.html', context)


def autocomplete(request):
    """API: Autocomplete gợi ý tìm kiếm"""
    query = request.GET.get('q', '').strip()
    limit = int(request.GET.get('limit', 10))

    if len(query) < 2:
        return JsonResponse({'suggestions': []})

    search_service = SearchService()
    suggestions = search_service.autocomplete(query, limit)
    return JsonResponse({'suggestions': suggestions})


def search_suggestions(request):
    """API: Từ khóa tìm kiếm phổ biến"""
    # Implement this method in SearchService if needed
    # For now, return empty list
    return JsonResponse({'suggestions': []})