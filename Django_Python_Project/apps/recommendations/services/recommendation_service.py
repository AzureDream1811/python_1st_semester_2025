"""
Service Gợi Ý Sản Phẩm cho ElectroShop
======================================

Module này chứa các service xử lý logic nghiệp vụ gợi ý sản phẩm:
- Tìm sản phẩm tương tự
- Gợi ý cá nhân hóa
- Sản phẩm thường mua cùng
- Sản phẩm trending
- Cập nhật độ tương đồng (Celery task)

Tác giả: ElectroShop Team
"""
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta


class RecommendationService:
    """
    Service quản lý các thuật toán gợi ý sản phẩm
    
    Cung cấp các phương thức:
    - get_similar_products: Tìm sản phẩm tương tự
    - get_personalized_recommendations: Gợi ý cá nhân hóa
    - get_frequently_bought_together: Sản phẩm mua cùng
    - get_trending_products: Sản phẩm trending
    - track_activity: Ghi nhận hoạt động
    - update_product_similarities: Cập nhật độ tương đồng
    """

    @staticmethod
    def get_similar_products(product_id, limit=10):
        """
        Tìm sản phẩm tương tự dựa trên danh mục và thuộc tính
        
        Args:
            product_id: ID sản phẩm cần tìm tương tự
            limit: Số lượng kết quả tối đa
            
        Returns:
            List[Product]: Danh sách sản phẩm tương tự
        """
        from apps.products.models import Product

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return []

        # Tìm sản phẩm cùng danh mục
        similar = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(pk=product_id)

        # Thêm sản phẩm cùng thương hiệu
        if product.brand:
            similar = similar | Product.objects.filter(
                brand=product.brand,
                is_active=True
            ).exclude(pk=product_id)

        # Sắp xếp theo rating
        similar = similar.distinct().order_by('-avg_rating', '-created_at')[:limit]

        return list(similar)

    @staticmethod
    def get_personalized_recommendations(user, limit=10):
        """
        Gợi ý cá nhân hóa dựa trên lịch sử người dùng
        
        Args:
            user: User object
            limit: Số lượng kết quả tối đa
            
        Returns:
            List[Product]: Danh sách sản phẩm gợi ý
        """
        from apps.products.models import Product
        from apps.recommendations.models import UserActivity

        if not user.is_authenticated:
            return RecommendationService.get_trending_products(limit)

        # Lấy danh mục từ lịch sử
        activities = UserActivity.objects.filter(user=user).values_list(
            'product__category_id', flat=True
        ).distinct()

        category_ids = list(filter(None, activities))

        if not category_ids:
            return RecommendationService.get_trending_products(limit)

        # Lấy sản phẩm đã mua
        purchased_ids = UserActivity.objects.filter(
            user=user,
            activity_type='purchase'
        ).values_list('product_id', flat=True)

        # Gợi ý sản phẩm chưa mua
        recommendations = Product.objects.filter(
            category_id__in=category_ids,
            is_active=True
        ).exclude(
            pk__in=purchased_ids
        ).order_by('-avg_rating', '-created_at')[:limit]

        return list(recommendations)

    @staticmethod
    def get_frequently_bought_together(product_id, limit=5):
        """
        Tìm sản phẩm thường được mua cùng
        
        Args:
            product_id: ID sản phẩm chính
            limit: Số lượng kết quả tối đa
            
        Returns:
            List[Product]: Danh sách sản phẩm mua cùng
        """
        from apps.products.models import Product
        from apps.orders.models import OrderItem

        # Tìm đơn hàng chứa sản phẩm này
        order_ids = OrderItem.objects.filter(
            product_id=product_id
        ).values_list('order_id', flat=True)

        # Tìm sản phẩm khác trong đơn hàng
        related_products = OrderItem.objects.filter(
            order_id__in=order_ids
        ).exclude(
            product_id=product_id
        ).values('product_id').annotate(
            count=Count('product_id')
        ).order_by('-count')[:limit]

        product_ids = [p['product_id'] for p in related_products]

        return list(Product.objects.filter(pk__in=product_ids, is_active=True))

    @staticmethod
    def get_trending_products(limit=10):
        """
        Lấy sản phẩm đang trending trong 7 ngày
        
        Args:
            limit: Số lượng kết quả tối đa
            
        Returns:
            List[Product]: Danh sách sản phẩm trending
        """
        from apps.products.models import Product
        from apps.recommendations.models import UserActivity

        since = timezone.now() - timedelta(days=7)

        trending = UserActivity.objects.filter(
            created_at__gte=since,
            product__isnull=False
        ).values('product_id').annotate(
            score=Count('id')
        ).order_by('-score')[:limit]

        product_ids = [t['product_id'] for t in trending]

        if not product_ids:
            return list(Product.objects.filter(is_active=True).order_by('-created_at')[:limit])

        return list(Product.objects.filter(pk__in=product_ids, is_active=True))

    @staticmethod
    def get_search_suggestions(limit=10):
        """
        Lấy gợi ý tìm kiếm phổ biến trong 30 ngày
        
        Args:
            limit: Số lượng kết quả tối đa
            
        Returns:
            List[str]: Danh sách từ khóa gợi ý
        """
        from apps.analytics.models import SearchLog

        since = timezone.now() - timedelta(days=30)

        popular = SearchLog.objects.filter(
            created_at__gte=since
        ).values('query').annotate(
            count=Count('id')
        ).order_by('-count')[:limit]

        return [p['query'] for p in popular]

    @staticmethod
    def track_activity(user, product_id, activity_type):
        """
        Ghi nhận hoạt động người dùng
        
        Args:
            user: User object
            product_id: ID sản phẩm
            activity_type: Loại hoạt động
        """
        from apps.recommendations.models import UserActivity

        if not user.is_authenticated:
            return

        UserActivity.objects.create(
            user=user,
            product_id=product_id,
            activity_type=activity_type
        )

    @staticmethod
    def update_product_similarities():
        """
        Cập nhật độ tương đồng sản phẩm (Celery task)
        
        Chạy định kỳ để cập nhật bảng ProductSimilarity
        """
        from apps.products.models import Product
        from apps.recommendations.models import ProductSimilarity

        products = Product.objects.filter(is_active=True)

        for product in products:
            similar = RecommendationService.get_similar_products(product.id, limit=20)

            # Xóa dữ liệu cũ
            ProductSimilarity.objects.filter(product=product).delete()

            # Tạo dữ liệu mới
            for i, sim_product in enumerate(similar):
                score = 1.0 - (i * 0.05)
                ProductSimilarity.objects.create(
                    product=product,
                    similar_product=sim_product,
                    score=max(score, 0.1)
                )
