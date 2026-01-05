"""
Search Service cho ElectroShop
Dịch vụ tìm kiếm sản phẩm với hỗ trợ tiếng Việt
"""
import re
from typing import List, Dict, Any, Optional
from django.db.models import Q, Count
from apps.products.models import Product


class SearchService:
    """
    Service xử lý tìm kiếm sản phẩm nâng cao
    
    Hỗ trợ:
    - Tìm kiếm có dấu và không dấu tiếng Việt
    - Lọc theo danh mục, giá, tồn kho, đánh giá
    - Phân trang kết quả
    - Gợi ý tìm kiếm (autocomplete)
    """

    # Bảng ánh xạ ký tự tiếng Việt có dấu -> không dấu
    # Dùng để chuẩn hóa text khi tìm kiếm
    VIETNAMESE_MAP = {
        # Chữ a
        'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
        'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
        'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
        # Chữ đ
        'đ': 'd',
        # Chữ e
        'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
        'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
        # Chữ i
        'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
        # Chữ o
        'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
        'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
        'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
        # Chữ u
        'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
        'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
        # Chữ y
        'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
    }

    @classmethod
    def normalize_vietnamese(cls, text: str) -> str:
        """
        Chuẩn hóa text tiếng Việt bằng cách bỏ dấu
        
        Ví dụ:
            "điện thoại" -> "dien thoai"
            "Máy Tính" -> "may tinh"
        
        Property 28: Tìm kiếm có dấu và không dấu phải trả về cùng kết quả
        
        Args:
            text: Chuỗi cần chuẩn hóa
            
        Returns:
            Chuỗi đã bỏ dấu và chuyển thành chữ thường
        """
        if not text:
            return ''

        text = text.lower()
        result = []
        for char in text:
            # Thay thế ký tự có dấu bằng không dấu, giữ nguyên nếu không có trong map
            result.append(cls.VIETNAMESE_MAP.get(char, char))
        return ''.join(result)

    @classmethod
    def autocomplete(cls, query: str, limit: int = 10) -> List[str]:
        """
        Lấy danh sách gợi ý tìm kiếm (autocomplete)
        
        Tìm các sản phẩm có tên chứa từ khóa và trả về danh sách tên sản phẩm

        Args:
            query: Từ khóa tìm kiếm
            limit: Số lượng gợi ý tối đa (mặc định 10)
            
        Returns:
            Danh sách tên sản phẩm gợi ý
        """
        # Không gợi ý nếu query quá ngắn
        if len(query) < 2:
            return []

        # Chuẩn hóa query để tìm cả có dấu và không dấu
        normalized_query = cls.normalize_vietnamese(query)

        # Tìm sản phẩm có tên chứa query (có dấu hoặc không dấu)
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(name__icontains=normalized_query),
            is_active=True  # Chỉ lấy sản phẩm đang bán
        ).values_list('name', flat=True)[:limit]

        return list(products)

    @classmethod
    def search_products(
            cls,
            query: str,
            filters: Optional[Dict[str, Any]] = None,
            sort: str = 'relevance'
    ):
        """
        Tìm kiếm sản phẩm với bộ lọc
        
        Hỗ trợ lọc theo:
        - category: Slug danh mục
        - brand: Slug thương hiệu
        - min_price: Giá tối thiểu
        - max_price: Giá tối đa
        - in_stock: Chỉ lấy sản phẩm còn hàng
        - rating: Đánh giá tối thiểu

        Args:
            query: Từ khóa tìm kiếm
            filters: Dict chứa các bộ lọc
            sort: Cách sắp xếp (relevance, price, -price, name, -created_at, -sold)
            
        Returns:
            QuerySet các sản phẩm thỏa mãn điều kiện
        """
        filters = filters or {}
        normalized_query = cls.normalize_vietnamese(query)

        # Query cơ bản: chỉ lấy sản phẩm đang bán
        queryset = Product.objects.filter(is_active=True)

        # Tìm kiếm theo text (tên và mô tả)
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(name__icontains=normalized_query) |
                Q(description__icontains=query) |
                Q(description__icontains=normalized_query)
            )

        # Áp dụng các bộ lọc

        # Lọc theo danh mục
        if filters.get('category'):
            queryset = queryset.filter(category__slug=filters['category'])

        # Lọc theo thương hiệu
        if filters.get('brand'):
            queryset = queryset.filter(brand__slug=filters['brand'])

        # Lọc theo giá tối thiểu
        if filters.get('min_price'):
            queryset = queryset.filter(price__gte=filters['min_price'])

        # Lọc theo giá tối đa
        if filters.get('max_price'):
            queryset = queryset.filter(price__lte=filters['max_price'])

        # Lọc chỉ sản phẩm còn hàng
        if filters.get('in_stock') == 'true':
            queryset = queryset.filter(stock__gt=0)

        # Lọc theo đánh giá tối thiểu
        if filters.get('rating'):
            # Sử dụng annotation để tính average_rating
            queryset = queryset.filter(sentiment_score__gte=float(filters['rating']) / 5)

        # Sắp xếp kết quả
        if sort == 'price':
            queryset = queryset.order_by('price')  # Giá tăng dần
        elif sort == '-price':
            queryset = queryset.order_by('-price')  # Giá giảm dần
        elif sort == 'name':
            queryset = queryset.order_by('name')  # Tên A-Z
        elif sort == '-name':
            queryset = queryset.order_by('-name')  # Tên Z-A
        elif sort == '-created_at':
            queryset = queryset.order_by('-created_at')  # Mới nhất
        elif sort == '-sold':
            queryset = queryset.order_by('-sold')  # Bán chạy nhất
        # Mặc định: relevance - giữ nguyên thứ tự từ query

        return queryset

    @classmethod
    def correct_spelling(cls, query: str) -> str:
        """
        Sửa lỗi chính tả phổ biến trong tiếng Việt
        
        Ánh xạ các từ không dấu phổ biến sang từ có dấu đúng

        Args:
            query: Từ khóa cần sửa
            
        Returns:
            Từ khóa đã sửa (hoặc giữ nguyên nếu không cần sửa)
        """
        # Bảng sửa lỗi cho các từ khóa phổ biến
        corrections = {
            'dien thoai': 'điện thoại',
            'may tinh': 'máy tính',
            'tu lanh': 'tủ lạnh',
            'may giat': 'máy giặt',
            'dieu hoa': 'điều hòa',
            'loa': 'loa',
            'tai nghe': 'tai nghe',
            'tivi': 'tivi',
            'laptop': 'laptop',
            'dong ho': 'đồng hồ',
            'camera': 'camera',
            'may anh': 'máy ảnh',
        }

        # Chuẩn hóa query và tìm trong bảng sửa lỗi
        normalized = cls.normalize_vietnamese(query.lower())
        return corrections.get(normalized, query)

    @classmethod
    def get_suggestions(cls, query: str) -> List[str]:
        """
        Lấy gợi ý tìm kiếm khi không có kết quả
        
        Trả về các từ khóa tìm kiếm phổ biến nhất
        
        Args:
            query: Từ khóa đã tìm (không có kết quả)
            
        Returns:
            Danh sách từ khóa gợi ý
        """
        from apps.analytics.models import SearchLog

        # Lấy top 5 từ khóa được tìm nhiều nhất
        popular = SearchLog.objects.values('query').annotate(
            count=Count('id')
        ).order_by('-count')[:5]

        return [s['query'] for s in popular]

    @classmethod
    def get_popular_searches(cls, limit: int = 10) -> List[str]:
        """
        Lấy danh sách từ khóa tìm kiếm phổ biến
        
        Dùng để hiển thị gợi ý trên trang tìm kiếm
        
        Args:
            limit: Số lượng từ khóa tối đa
            
        Returns:
            Danh sách từ khóa phổ biến
        """
        from apps.analytics.models import SearchLog

        # Lấy top từ khóa được tìm nhiều nhất
        popular = SearchLog.objects.values('query').annotate(
            count=Count('id')
        ).order_by('-count')[:limit]

        return [s['query'] for s in popular]

    @classmethod
    def highlight_keywords(cls, text: str, keywords: List[str]) -> str:
        """
        Highlight từ khóa trong kết quả tìm kiếm
        
        Bọc các từ khóa trong thẻ <mark> để hiển thị nổi bật

        Args:
            text: Văn bản cần highlight
            keywords: Danh sách từ khóa cần highlight
            
        Returns:
            Văn bản đã highlight từ khóa
        """
        if not text or not keywords:
            return text

        for keyword in keywords:
            # Tạo pattern không phân biệt hoa thường
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            # Thay thế bằng từ khóa được bọc trong <mark>
            text = pattern.sub(f'<mark>{keyword}</mark>', text)

        return text

    @classmethod
    def log_search(cls, query: str, user=None, results_count: int = 0, clicked_product=None):
        """
        Ghi log lịch sử tìm kiếm
        
        Lưu thông tin tìm kiếm vào database để phân tích

        Args:
            query: Từ khóa đã tìm
            user: User thực hiện tìm kiếm (None nếu anonymous)
            results_count: Số kết quả tìm được
            clicked_product: Sản phẩm user đã click (nếu có)
        """
        from apps.analytics.models import SearchLog

        SearchLog.objects.create(
            user=user,
            query=query,
            results_count=results_count,
            clicked_product=clicked_product
        )
