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

    # Sort
    sort = request.GET.get('sort', 'relevance')

    if query:
        # Log search
        SearchService.log_search(query, request.user if request.user.is_authenticated else None)

        # Search with Elasticsearch or fallback to DB
        results = SearchService.search_products(query, filters, sort)
    else:
        results = Product.objects.filter(is_active=True)

        # Apply filters
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

    # Pagination
    paginator = Paginator(results, 20)
    page = request.GET.get('page', 1)
    products = paginator.get_page(page)

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

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return JSON for AJAX requests
        return JsonResponse({
            'results': [
                {
                    'id': p.id,
                    'name': p.name,
                    'price': float(p.price),
                    'image': p.image.url if p.image else '',
                    'url': p.get_absolute_url(),
                }
                for p in products
            ],
            'total': paginator.count,
            'page': products.number,
            'pages': paginator.num_pages,
        })

    return render(request, 'search/search_results.html', context)


def autocomplete(request):
    """API: Autocomplete gợi ý tìm kiếm"""
    query = request.GET.get('q', '').strip()
    limit = int(request.GET.get('limit', 10))

    if len(query) < 2:
        return JsonResponse({'suggestions': []})

    suggestions = SearchService.autocomplete(query, limit)
    return JsonResponse({'suggestions': suggestions})


def search_suggestions(request):
    """API: Từ khóa tìm kiếm phổ biến"""
    # Implement this method in SearchService if needed
    # For now, return empty list
    return JsonResponse({'suggestions': []})