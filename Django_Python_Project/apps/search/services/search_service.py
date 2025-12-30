"""
Search Service for ElectroShop
Elasticsearch-based search with Vietnamese support
"""
import re
import unicodedata
from typing import List, Dict, Any, Optional
from django.db.models import Q
from apps.products.models import Product


class SearchService:
    """Service for advanced product search"""

    # Vietnamese character mapping for normalization
    VIETNAMESE_MAP = {
        'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
        'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
        'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
        'đ': 'd',
        'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
        'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
        'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
        'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
        'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
        'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
        'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
        'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
        'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
    }

    def normalize_vietnamese(self, text: str) -> str:
        """
        Normalize Vietnamese text by removing diacritics
        Property 28: Search with/without diacritics must return same results
        """
        if not text:
            return ''

        text = text.lower()
        result = []
        for char in text:
            result.append(self.VIETNAMESE_MAP.get(char, char))
        return ''.join(result)

    def autocomplete(self, query: str, limit: int = 10) -> List[str]:
        """
        Get autocomplete suggestions
        Property 27: Must return results for queries with 2+ characters
        """
        if len(query) < 2:
            return []

        normalized_query = self.normalize_vietnamese(query)

        # Get product names matching query
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(name__icontains=normalized_query),
            is_active=True
        ).values_list('name', flat=True)[:limit]

        return list(products)

    def search_products(
            self,
            query: str,
            filters: Optional[Dict[str, Any]] = None,
            page: int = 1,
            page_size: int = 20
    ) -> Dict[str, Any]:
        """
        Search products with filters
        Property 29: All results must satisfy filter conditions
        """
        filters = filters or {}
        normalized_query = self.normalize_vietnamese(query)

        # Base query
        queryset = Product.objects.filter(is_active=True)

        # Text search
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(name__icontains=normalized_query) |
                Q(description__icontains=query) |
                Q(description__icontains=normalized_query)
            )

        # Apply filters
        if 'category' in filters:
            queryset = queryset.filter(category_id=filters['category'])

        if 'min_price' in filters:
            queryset = queryset.filter(price__gte=filters['min_price'])

        if 'max_price' in filters:
            queryset = queryset.filter(price__lte=filters['max_price'])

        if 'in_stock' in filters and filters['in_stock']:
            queryset = queryset.filter(stock__gt=0)

        if 'min_rating' in filters:
            queryset = queryset.filter(average_rating__gte=filters['min_rating'])

        # Pagination
        total = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        products = queryset[start:end]

        return {
            'products': list(products),
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }

    def correct_spelling(self, query: str) -> str:
        """
        Correct common spelling mistakes
        Property 30: Corrected query should have edit distance <= 2
        """
        # Simple correction rules for common Vietnamese typos
        corrections = {
            'dien thoai': 'điện thoại',
            'may tinh': 'máy tính',
            'tu lanh': 'tủ lạnh',
            'may giat': 'máy giặt',
            'dieu hoa': 'điều hòa',
            'loa': 'loa',
            'tai nghe': 'tai nghe',
        }

        normalized = self.normalize_vietnamese(query.lower())
        return corrections.get(normalized, query)

    # def get_suggestions(self, query: str) -> List[str]:
    #     """Get search suggestions when no results found"""
    #     # Get popular searches
    #     from apps.analytics.models import SearchLog
    #
    #     popular = SearchLog.objects.values('query').annotate(
    #         count=models.Count('id')
    #     ).order_by('-count')[:5]
    #
    #     return [s['query'] for s in popular]

    def highlight_keywords(self, text: str, keywords: List[str]) -> str:
        """
        Highlight keywords in search results
        Property: Keywords must be wrapped in <mark> tags
        """
        if not text or not keywords:
            return text

        for keyword in keywords:
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            text = pattern.sub(f'<mark>{keyword}</mark>', text)

        return text

    # def log_search(self, query: str, results_count: int, user=None, clicked_product=None):
    #     """
    #     Log search query
    #     Property 31: Search history must be saved
    #     """
    #     from apps.analytics.models import SearchLog
    #
    #     SearchLog.objects.create(
    #         user=user,
    #         query=query,
    #         results_count=results_count,
    #         clicked_product=clicked_product
    #     )
