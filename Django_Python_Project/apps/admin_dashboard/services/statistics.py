"""
Dashboard Statistics Service
Cung cấp các hàm tính toán thống kê cho Admin Dashboard
"""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any
from django.db.models import Sum, Count, Avg, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.contrib.auth.models import User

from apps.orders.models import Order, OrderItem
from apps.products.models import Product, Category
from apps.reviews.models import Review


class DashboardStatistics:
    """Service class để tính toán các thống kê cho dashboard"""

    # === REVENUE STATISTICS ===

    def get_revenue_stats(self, start_date=None, end_date=None) -> Dict[str, Any]:
        """
        Tính toán doanh thu trong khoảng thời gian
        Property 1: Tổng doanh thu = tổng giá trị đơn hàng completed/delivered
        """
        if not start_date:
            start_date = timezone.now().replace(day=1).date()
        if not end_date:
            end_date = timezone.now().date()

        completed_orders = Order.objects.filter(
            status__in=['completed', 'delivered'],
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )

        total_revenue = completed_orders.aggregate(
            total=Sum('total')
        )['total'] or Decimal('0')

        order_count = completed_orders.count()

        return {
            'total_revenue': total_revenue,
            'order_count': order_count,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        }

    def get_daily_revenue(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Lấy doanh thu theo ngày cho biểu đồ
        """
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)

        daily_revenue = Order.objects.filter(
            status__in=['completed', 'delivered'],
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            revenue=Sum('total')
        ).order_by('date')

        return list(daily_revenue)

    def get_daily_revenue_chart_data(self, days: int = 30) -> Dict[str, Any]:
        """Dữ liệu biểu đồ doanh thu theo ngày"""
        daily_data = self.get_daily_revenue(days)

        labels = [d['date'].strftime('%d/%m') for d in daily_data]
        values = [float(d['revenue'] or 0) for d in daily_data]

        return {
            'labels': labels,
            'datasets': [{
                'label': 'Doanh thu (VNĐ)',
                'data': values,
                'borderColor': '#4CAF50',
                'backgroundColor': 'rgba(76, 175, 80, 0.1)',
                'fill': True
            }]
        }

    # === ORDER STATISTICS ===

    def get_order_stats(self) -> Dict[str, Any]:
        """
        Thống kê đơn hàng theo trạng thái
        Property 2: Số lượng theo trạng thái = count thực tế trong DB
        """
        status_counts = Order.objects.values('status').annotate(
            count=Count('id')
        )

        stats = {item['status']: item['count'] for item in status_counts}
        total = sum(stats.values())

        return {
            'total': total,
            'by_status': stats
        }

    def get_order_status_chart_data(self) -> Dict[str, Any]:
        """Dữ liệu biểu đồ trạng thái đơn hàng"""
        stats = self.get_order_stats()

        status_labels = {
            'pending': 'Chờ xác nhận',
            'confirmed': 'Đã xác nhận',
            'processing': 'Đang xử lý',
            'shipping': 'Đang giao',
            'delivered': 'Đã giao',
            'completed': 'Hoàn thành',
            'cancelled': 'Đã hủy',
            'refunded': 'Hoàn tiền'
        }

        colors = {
            'pending': '#FFC107',
            'confirmed': '#2196F3',
            'processing': '#9C27B0',
            'shipping': '#00BCD4',
            'delivered': '#4CAF50',
            'completed': '#8BC34A',
            'cancelled': '#F44336',
            'refunded': '#9E9E9E'
        }

        labels = []
        values = []
        bg_colors = []

        for status, count in stats['by_status'].items():
            labels.append(status_labels.get(status, status))
            values.append(count)
            bg_colors.append(colors.get(status, '#666'))

        return {
            'labels': labels,
            'datasets': [{
                'data': values,
                'backgroundColor': bg_colors
            }]
        }

    def get_recent_orders(self, limit: int = 10) -> List[Order]:
        """Lấy đơn hàng gần đây"""
        return Order.objects.select_related('user').order_by('-created_at')[:limit]

    def filter_orders_by_date(self, start_date, end_date):
        """
        Lọc đơn hàng theo khoảng thời gian
        Property 7: Tất cả orders trả về có created_at trong khoảng
        """
        return Order.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )

    # === SENTIMENT STATISTICS ===

    def get_sentiment_stats(self) -> Dict[str, int]:
        """
        Thống kê sentiment từ reviews
        Property 3: Số lượng theo sentiment = count thực tế
        """
        sentiment_counts = Review.objects.filter(
            is_approved=True
        ).values('sentiment').annotate(
            count=Count('id')
        )

        stats = {
            'positive': 0,
            'negative': 0,
            'neutral': 0
        }

        for item in sentiment_counts:
            if item['sentiment'] in stats:
                stats[item['sentiment']] = item['count']

        stats['total'] = sum(stats.values())
        return stats

    def get_product_sentiment(self, product_id: int) -> Dict[str, int]:
        """
        Thống kê sentiment cho một sản phẩm
        Property 8: Số lượng theo sentiment của product = count thực tế
        """
        sentiment_counts = Review.objects.filter(
            product_id=product_id,
            is_approved=True
        ).values('sentiment').annotate(
            count=Count('id')
        )

        stats = {
            'positive': 0,
            'negative': 0,
            'neutral': 0
        }

        for item in sentiment_counts:
            if item['sentiment'] in stats:
                stats[item['sentiment']] = item['count']

        return stats

    def get_sentiment_chart_data(self) -> Dict[str, Any]:
        """Dữ liệu biểu đồ sentiment"""
        stats = self.get_sentiment_stats()

        return {
            'labels': ['Tích cực', 'Tiêu cực', 'Trung lập'],
            'datasets': [{
                'data': [
                    stats['positive'],
                    stats['negative'],
                    stats['neutral']
                ],
                'backgroundColor': ['#4CAF50', '#F44336', '#9E9E9E']
            }]
        }

    # === PRODUCT STATISTICS ===

    def get_top_products(self, limit: int = 10) -> List[Product]:
        """
        Lấy sản phẩm bán chạy nhất
        Property 4: Sản phẩm đầu tiên có sold >= tất cả sản phẩm khác
        """
        return Product.objects.filter(
            is_active=True
        ).order_by('-sold')[:limit]

    def get_products_sorted_by_sentiment(self, ascending: bool = False):
        """
        Sắp xếp sản phẩm theo sentiment score
        Property 9: Mỗi product có sentiment_score >= product tiếp theo (desc)
        """
        order = 'sentiment_score' if ascending else '-sentiment_score'
        return Product.objects.filter(is_active=True).order_by(order)

    @staticmethod
    def needs_warning(product: Product) -> bool:
        """
        Xác định sản phẩm cần cảnh báo
        Property 10: Nếu sentiment_score < 0 thì return True
        """
        return product.sentiment_score < 0

    def get_category_revenue(self) -> List[Dict[str, Any]]:
        """Doanh thu theo danh mục"""
        category_revenue = OrderItem.objects.filter(
            order__status__in=['completed', 'delivered']
        ).values(
            'product__category__name'
        ).annotate(
            revenue=Sum('price')
        ).order_by('-revenue')

        return list(category_revenue)

    def get_category_revenue_chart_data(self) -> Dict[str, Any]:
        """Dữ liệu biểu đồ doanh thu theo danh mục"""
        data = self.get_category_revenue()

        labels = [d['product__category__name'] or 'Khác' for d in data]
        values = [float(d['revenue'] or 0) for d in data]

        colors = ['#4CAF50', '#2196F3', '#FFC107', '#9C27B0', '#FF5722',
                  '#00BCD4', '#E91E63', '#8BC34A', '#FF9800', '#607D8B']

        return {
            'labels': labels,
            'datasets': [{
                'label': 'Doanh thu (VNĐ)',
                'data': values,
                'backgroundColor': colors[:len(values)]
            }]
        }

    # === CUSTOMER STATISTICS ===

    def get_customer_count(self) -> int:
        """Đếm số khách hàng đã đăng ký"""
        return User.objects.filter(is_active=True, is_staff=False).count()

    def get_active_product_count(self) -> int:
        """Đếm số sản phẩm đang hoạt động"""
        return Product.objects.filter(is_active=True).count()

    # === REVENUE REPORT ===

    def get_revenue_by_payment_method(self, start_date, end_date) -> Dict[str, Decimal]:
        """
        Doanh thu theo phương thức thanh toán
        Property 11: Tổng theo payment_method = sum thực tế
        """
        revenue_by_method = Order.objects.filter(
            status__in=['completed', 'delivered'],
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).values('payment_method').annotate(
            revenue=Sum('total')
        )

        return {
            item['payment_method']: item['revenue'] or Decimal('0')
            for item in revenue_by_method
        }

    def get_top_revenue_products(self, start_date, end_date, limit: int = 10):
        """Sản phẩm có doanh thu cao nhất"""
        return OrderItem.objects.filter(
            order__status__in=['completed', 'delivered'],
            order__created_at__date__gte=start_date,
            order__created_at__date__lte=end_date
        ).values(
            'product__name', 'product__id'
        ).annotate(
            revenue=Sum('price'),
            quantity=Sum('quantity')
        ).order_by('-revenue')[:limit]

    def get_revenue_report(self, start_date, end_date) -> Dict[str, Any]:
        """Báo cáo doanh thu đầy đủ"""
        current_stats = self.get_revenue_stats(start_date, end_date)

        # Tính kỳ trước để so sánh
        period_days = (end_date - start_date).days
        prev_end = start_date - timedelta(days=1)
        prev_start = prev_end - timedelta(days=period_days)
        prev_stats = self.get_revenue_stats(prev_start, prev_end)

        # Tính % thay đổi
        if prev_stats['total_revenue'] > 0:
            change_percent = (
                    (current_stats['total_revenue'] - prev_stats['total_revenue'])
                    / prev_stats['total_revenue'] * 100
            )
        else:
            change_percent = 100 if current_stats['total_revenue'] > 0 else 0

        return {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'total_revenue': float(current_stats['total_revenue']),
            'order_count': current_stats['order_count'],
            'by_payment_method': {
                k: float(v) for k, v in
                self.get_revenue_by_payment_method(start_date, end_date).items()
            },
            'top_products': list(self.get_top_revenue_products(start_date, end_date)),
            'comparison': {
                'previous_revenue': float(prev_stats['total_revenue']),
                'change_percent': round(change_percent, 2)
            }
        }

    # === DASHBOARD SUMMARY ===

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Lấy tất cả thống kê cho dashboard"""
        revenue_stats = self.get_revenue_stats()
        order_stats = self.get_order_stats()
        sentiment_stats = self.get_sentiment_stats()

        return {
            'revenue': revenue_stats,
            'orders': order_stats,
            'customers': self.get_customer_count(),
            'products': self.get_active_product_count(),
            'sentiment': sentiment_stats,
            'top_products': list(self.get_top_products(5).values('name', 'sold', 'price', 'sale_price')),
            'recent_orders': list(self.get_recent_orders(5).values(
                'order_number', 'full_name', 'total', 'status', 'created_at'
            ))
        }
