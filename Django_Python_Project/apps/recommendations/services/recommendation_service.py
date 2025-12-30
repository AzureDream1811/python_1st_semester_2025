from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta


class RecommendationService:
    """Service for product recommendations"""

    @staticmethod
    def get_similar_products(product_id, limit=10):
        """Get similar products based on category and attributes"""
        from apps.products.models import Product

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return []

        # Find products in same category, excluding current product
        similar = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(pk=product_id)

        # Also include products from same brand
        if product.brand:
            similar = similar | Product.objects.filter(
                brand=product.brand,
                is_active=True
            ).exclude(pk=product_id)

        # Order by rating and limit
        similar = similar.distinct().order_by('-avg_rating', '-created_at')[:limit]

        return list(similar)

    @staticmethod
    def get_personalized_recommendations(user, limit=10):
        """Get personalized recommendations based on user history"""
        from apps.products.models import Product
        from apps.recommendations.models import UserActivity

        if not user.is_authenticated:
            return RecommendationService.get_trending_products(limit)

        # Get user's viewed and purchased categories
        activities = UserActivity.objects.filter(user=user).values_list(
            'product__category_id', flat=True
        ).distinct()

        category_ids = list(activities)

        if not category_ids:
            return RecommendationService.get_trending_products(limit)

        # Get products from those categories that user hasn't purchased
        purchased_ids = UserActivity.objects.filter(
            user=user,
            activity_type='purchase'
        ).values_list('product_id', flat=True)

        recommendations = Product.objects.filter(
            category_id__in=category_ids,
            is_active=True
        ).exclude(
            pk__in=purchased_ids
        ).order_by('-avg_rating', '-created_at')[:limit]

        return list(recommendations)

    @staticmethod
    def get_frequently_bought_together(product_id, limit=5):
        """Get products frequently bought together"""
        from apps.products.models import Product
        from apps.orders.models import OrderItem

        # Find orders containing this product
        order_ids = OrderItem.objects.filter(
            product_id=product_id
        ).values_list('order_id', flat=True)

        # Find other products in those orders
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
        """Get trending products based on recent views and purchases"""
        from apps.products.models import Product
        from apps.recommendations.models import UserActivity

        # Last 7 days
        since = timezone.now() - timedelta(days=7)

        # Count activities per product
        trending = UserActivity.objects.filter(
            created_at__gte=since
        ).values('product_id').annotate(
            score=Count('id')
        ).order_by('-score')[:limit]

        product_ids = [t['product_id'] for t in trending]

        if not product_ids:
            # Fallback to newest products
            return list(Product.objects.filter(is_active=True).order_by('-created_at')[:limit])

        return list(Product.objects.filter(pk__in=product_ids, is_active=True))

    # @staticmethod
    # def get_search_suggestions(limit=10):
    #     """Get popular search terms"""
    #     from apps.analytics.models import SearchLog
    #
    #     # Last 30 days
    #     since = timezone.now() - timedelta(days=30)
    #
    #     popular = SearchLog.objects.filter(
    #         created_at__gte=since
    #     ).values('query').annotate(
    #         count=Count('id')
    #     ).order_by('-count')[:limit]
    #
    #     return [p['query'] for p in popular]

    @staticmethod
    def track_activity(user, product_id, activity_type):
        """Track user activity for recommendations"""
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
        """Update pre-computed product similarities (run as Celery task)"""
        from apps.products.models import Product
        from apps.recommendations.models import ProductSimilarity

        products = Product.objects.filter(is_active=True)

        for product in products:
            similar = RecommendationService.get_similar_products(product.id, limit=20)

            # Clear old similarities
            ProductSimilarity.objects.filter(product=product).delete()

            # Create new similarities
            for i, sim_product in enumerate(similar):
                score = 1.0 - (i * 0.05)  # Decreasing score
                ProductSimilarity.objects.create(
                    product=product,
                    similar_product=sim_product,
                    score=score
                )
