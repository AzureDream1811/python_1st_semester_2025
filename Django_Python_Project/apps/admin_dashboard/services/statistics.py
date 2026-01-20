"""
Dashboard Statistics Service
Cung cấp các hàm tính toán thống kê cho Admin Dashboard
"""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any
from django.db.models.query import QuerySet
from django.db.models import Sum, Count, Avg, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.contrib.auth.models import User

from apps.orders.models import Order, OrderItem
from apps.products.models import Product, Category
from apps.reviews.models import Review
from apps.promotions.models import Voucher, VoucherUsage, FlashSale


class DashboardStatistics:
    """Service class để tính toán các thống kê cho dashboard"""

    PAID_STATUS = 'paid'

    # === REVENUE STATISTICS ===

    def get_revenue_stats(self, start_date=None, end_date=None) -> Dict[str, Any]:
        """
        Tính toán doanh thu trong khoảng thời gian
        Chỉ tính đơn hàng đã xác nhận thanh toán (payment_status='paid')
        """
        if not start_date:
            start_date = timezone.now().replace(day=1).date()
        if not end_date:
            end_date = timezone.now().date()

        # Chỉ tính đơn hàng đã thanh toán
        paid_orders = Order.objects.filter(
            payment_status=self.PAID_STATUS,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).exclude(status__in=['cancelled', 'refunded'])

        total_revenue = paid_orders.aggregate(
            total=Sum('total')
        )['total'] or Decimal('0')

        order_count = paid_orders.count()

        return {
            'total_revenue': total_revenue,
            'order_count': order_count,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        }

    def get_daily_revenue(self, start_date=None, end_date=None) -> List[Dict[str, Any]]:
        """
        Lấy doanh thu theo ngày cho biểu đồ
        Chỉ tính đơn hàng đã xác nhận thanh toán (payment_status='paid')
        """
        if not end_date:
            end_date = timezone.now().date()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        # Chỉ tính doanh thu từ đơn hàng đã thanh toán
        daily_revenue = Order.objects.filter(
            payment_status=self.PAID_STATUS,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).exclude(
            status__in=['cancelled', 'refunded']
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            revenue=Sum('total')
        ).order_by('date')

        return list(daily_revenue)

    def get_daily_revenue_chart_data(self, start_date=None, end_date=None) -> Dict[str, Any]:
        """Dữ liệu biểu đồ doanh thu theo ngày - điền đầy đủ tất cả ngày trong khoảng"""
        if not end_date:
            end_date = timezone.now().date()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        daily_data = self.get_daily_revenue(start_date, end_date)

        # Nếu không có data trong khoảng, thử lấy tất cả paid orders
        if not daily_data:
            # Lấy tất cả paid orders và group theo ngày
            all_paid = list(Order.objects.filter(
                payment_status=self.PAID_STATUS
            ).exclude(
                status__in=['cancelled', 'refunded']
            ).annotate(
                date=TruncDate('created_at')
            ).values('date').annotate(
                revenue=Sum('total')
            ).order_by('date'))

            if all_paid:
                # Tìm min/max date
                dates = [d['date'] for d in all_paid if d['date']]
                if dates:
                    start_date = min(dates)
                    end_date = max(dates)
                    daily_data = all_paid

        # Đảm bảo start_date và end_date không None
        if not start_date or not end_date:
            # Không có data nào - trả về empty
            return {
                'labels': [],
                'data': [],
                'total': 0
            }

        # Tạo dict để tra cứu nhanh
        revenue_by_date = {d['date']: float(d['revenue'] or 0) for d in daily_data}

        # Tạo danh sách tất cả các ngày trong khoảng
        labels = []
        values = []
        current_date = start_date
        while current_date <= end_date:
            labels.append(current_date.strftime('%d/%m'))
            values.append(revenue_by_date.get(current_date, 0))
            current_date += timedelta(days=1)

        # Thêm total revenue để hiển thị
        total_revenue = sum(values)

        return {
            'labels': labels,
            'data': values,
            'total': total_revenue
        }

    # === ORDER STATISTICS ===

    def get_order_stats(self) -> Dict[str, Any]:
        """
        Thống kê đơn hàng theo trạng thái
        Số lượng theo trạng thái = count thực tế trong DB
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

    def get_order_status_chart_data(self, start_date=None, end_date=None) -> Dict[str, Any]:
        """Dữ liệu biểu đồ trạng thái đơn hàng"""
        if start_date and end_date:
            orders = Order.objects.filter(
                created_at__date__gte=start_date,
                created_at__date__lte=end_date
            )
            status_counts = orders.values('status').annotate(count=Count('id'))
            by_status = {item['status']: item['count'] for item in status_counts}

            # Nếu không có data trong period, sử dụng all orders
            if not by_status:
                stats = self.get_order_stats()
            else:
                stats = {'by_status': by_status}
        else:
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
            'data': values,
            'backgroundColor': bg_colors
        }

    def get_recent_orders(self, limit: int = 10) -> QuerySet:
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

    def get_top_products(self, limit: int = 10) -> QuerySet:
        """
        Lấy sản phẩm bán chạy nhất
        Sản phẩm đầu tiên có sold >= tất cả sản phẩm khác
        """
        return Product.objects.filter(
            is_active=True
        ).order_by('-sold')[:limit]

    def get_products_sorted_by_sentiment(self, ascending: bool = False):
        """
        Sắp xếp sản phẩm theo sentiment score
        Mỗi product có sentiment_score >= product tiếp theo (desc)
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
        """Doanh thu theo danh mục - chỉ tính đơn đã thanh toán"""
        category_revenue = OrderItem.objects.filter(
            order__payment_status=self.PAID_STATUS
        ).exclude(
            order__status__in=['cancelled', 'refunded']
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
        Chỉ tính đơn đã thanh toán
        """
        revenue_by_method = Order.objects.filter(
            payment_status=self.PAID_STATUS,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).exclude(
            status__in=['cancelled', 'refunded']
        ).values('payment_method').annotate(
            revenue=Sum('total')
        )

        return {
            item['payment_method']: item['revenue'] or Decimal('0')
            for item in revenue_by_method
        }

    def get_top_revenue_products(self, start_date, end_date, limit: int = 10):
        """Sản phẩm có doanh thu cao nhất - chỉ tính đơn đã thanh toán"""
        return OrderItem.objects.filter(
            order__payment_status=self.PAID_STATUS,
            order__created_at__date__gte=start_date,
            order__created_at__date__lte=end_date
        ).exclude(
            order__status__in=['cancelled', 'refunded']
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

    # === TIME-BASED STATISTICS ===

    def get_time_based_stats(self, period: str = 'month', custom_start=None, custom_end=None) -> Dict[str, Any]:
        """
        Thống kê theo mốc thời gian
        period: 'today', 'week', 'month', 'year', 'custom'
        """
        today = timezone.now().date()

        if period == 'today':
            start_date = today
            end_date = today
            period_label = 'Hôm nay'
        elif period == 'week':
            start_date = today - timedelta(days=7)
            end_date = today
            period_label = '7 ngày qua'
        elif period == 'month':
            start_date = today.replace(day=1)
            end_date = today
            period_label = 'Tháng này'
        elif period == 'year':
            start_date = today.replace(month=1, day=1)
            end_date = today
            period_label = 'Năm nay'
        elif period == 'custom' and custom_start and custom_end:
            start_date = custom_start
            end_date = custom_end
            period_label = f'{start_date.strftime("%d/%m/%Y")} - {end_date.strftime("%d/%m/%Y")}'
        else:
            start_date = today.replace(day=1)
            end_date = today
            period_label = 'Tháng này'

        revenue_stats = self.get_revenue_stats(start_date, end_date)

        orders = Order.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )

        return {
            'period': period,
            'period_label': period_label,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'total_revenue': revenue_stats['total_revenue'],
            'total_orders': orders.count(),
            'completed_orders': orders.filter(status__in=['completed', 'delivered']).count(),
            'cancelled_orders': orders.filter(status='cancelled').count(),
            'avg_order_value': revenue_stats['total_revenue'] / revenue_stats['order_count'] if revenue_stats[
                                                                                                    'order_count'] > 0 else Decimal(
                '0'),
        }

    # === PROMOTION REVENUE STATISTICS ===

    def get_promotion_stats(self, start_date=None, end_date=None) -> Dict[str, Any]:
        """
        Thống kê doanh thu theo chương trình khuyến mãi
        """
        if not start_date:
            start_date = timezone.now().replace(day=1).date()
        if not end_date:
            end_date = timezone.now().date()

        voucher_usage = VoucherUsage.objects.filter(
            used_at__date__gte=start_date,
            used_at__date__lte=end_date
        )

        total_discount = voucher_usage.aggregate(
            total=Sum('discount_amount')
        )['total'] or Decimal('0')

        voucher_stats = voucher_usage.values(
            'voucher__code', 'voucher__name'
        ).annotate(
            usage_count=Count('id'),
            total_discount=Sum('discount_amount')
        ).order_by('-total_discount')[:10]

        active_flash_sales = FlashSale.objects.filter(
            is_active=True,
            start_time__lte=timezone.now(),
            end_time__gte=timezone.now()
        ).count()

        flash_sales = FlashSale.objects.filter(
            start_time__date__gte=start_date,
            end_time__date__lte=end_date
        )

        flash_sale_revenue = Decimal('0')
        original_revenue = Decimal('0')
        for fs in flash_sales:
            if fs.sold_count > 0:
                effective_price = fs.get_effective_sale_price()
                flash_sale_revenue += effective_price * fs.sold_count
                original_revenue += fs.product.price * fs.sold_count

        discount_given = original_revenue - flash_sale_revenue

        total_flash_sold = flash_sales.aggregate(
            total=Sum('sold_count')
        )['total'] or 0

        return {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'voucher': {
                'total_discount': total_discount,
                'usage_count': voucher_usage.count(),
                'top_vouchers': list(voucher_stats)
            },
            'flash_sale': {
                'active_count': active_flash_sales,
                'total_revenue': flash_sale_revenue,
                'original_revenue': original_revenue,
                'discount_given': discount_given,
                'total_sold': total_flash_sold,
                'total_campaigns': flash_sales.count()
            }
        }

    def get_monthly_comparison(self, months: int = 6) -> List[Dict[str, Any]]:
        """So sánh doanh thu theo tháng"""
        today = timezone.now().date()
        monthly_data = []

        for i in range(months):
            if i == 0:
                end_date = today
                start_date = today.replace(day=1)
            else:
                month = today.month - i
                year = today.year
                while month <= 0:
                    month += 12
                    year -= 1

                start_date = today.replace(year=year, month=month, day=1)
                if month == 12:
                    end_date = start_date.replace(year=year + 1, month=1, day=1) - timedelta(days=1)
                else:
                    end_date = start_date.replace(month=month + 1, day=1) - timedelta(days=1)

            stats = self.get_revenue_stats(start_date, end_date)
            monthly_data.append({
                'month': start_date.strftime('%m/%Y'),
                'month_name': start_date.strftime('%B %Y'),
                'revenue': float(stats['total_revenue']),
                'orders': stats['order_count']
            })

        return list(reversed(monthly_data))

    # === DASHBOARD SUMMARY ===

    def _calculate_percentage_change(self, current: float, previous: float) -> float:
        """Tính phần trăm thay đổi so với kỳ trước"""
        if previous > 0:
            return round(((current - previous) / previous) * 100, 1)
        return 100.0 if current > 0 else 0.0

    def _get_previous_period_dates(self, period: str, custom_start=None, custom_end=None):
        """Tính khoảng thời gian kỳ trước để so sánh"""
        today = timezone.now().date()

        if period == 'today':
            # So sánh với hôm qua
            prev_start = today - timedelta(days=1)
            prev_end = today - timedelta(days=1)
        elif period == 'week':
            # So sánh với 7 ngày trước đó
            prev_start = today - timedelta(days=14)
            prev_end = today - timedelta(days=8)
        elif period == 'month':
            # So sánh với tháng trước
            first_day = today.replace(day=1)
            prev_end = first_day - timedelta(days=1)
            prev_start = prev_end.replace(day=1)
        elif period == 'year':
            # So sánh với năm trước
            prev_start = today.replace(year=today.year - 1, month=1, day=1)
            prev_end = today.replace(year=today.year - 1, month=12, day=31)
        elif period == 'custom' and custom_start and custom_end:
            # So sánh với khoảng thời gian tương đương trước đó
            days_diff = (custom_end - custom_start).days + 1
            prev_end = custom_start - timedelta(days=1)
            prev_start = prev_end - timedelta(days=days_diff - 1)
        else:
            # Mặc định so sánh với tháng trước
            first_day = today.replace(day=1)
            prev_end = first_day - timedelta(days=1)
            prev_start = prev_end.replace(day=1)

        return prev_start, prev_end

    def _get_period_order_count(self, start_date, end_date) -> int:
        """Đếm số đơn hàng trong khoảng thời gian"""
        return Order.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).count()

    def _get_period_customer_count(self, start_date, end_date) -> int:
        """Đếm số khách hàng mới trong khoảng thời gian"""
        return User.objects.filter(
            is_active=True,
            is_staff=False,
            date_joined__date__gte=start_date,
            date_joined__date__lte=end_date
        ).count()

    def _get_period_product_count(self, start_date, end_date) -> int:
        """Đếm số sản phẩm mới trong khoảng thời gian"""
        return Product.objects.filter(
            is_active=True,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).count()

    def get_dashboard_summary(self, period: str = 'month', custom_start=None, custom_end=None) -> Dict[str, Any]:
        """Lấy tất cả thống kê cho dashboard"""
        time_stats = self.get_time_based_stats(period, custom_start, custom_end)
        order_stats = self.get_order_stats()
        sentiment_stats = self.get_sentiment_stats()
        promotion_stats = self.get_promotion_stats()

        # Lấy thông tin kỳ trước để so sánh
        prev_start, prev_end = self._get_previous_period_dates(period, custom_start, custom_end)

        # Lấy khoảng thời gian hiện tại từ time_stats
        today = timezone.now().date()
        if period == 'today':
            current_start = today
            current_end = today
        elif period == 'week':
            current_start = today - timedelta(days=7)
            current_end = today
        elif period == 'month':
            current_start = today.replace(day=1)
            current_end = today
        elif period == 'year':
            current_start = today.replace(month=1, day=1)
            current_end = today
        elif period == 'custom' and custom_start and custom_end:
            current_start = custom_start
            current_end = custom_end
        else:
            current_start = today.replace(day=1)
            current_end = today

        # Tính toán số liệu kỳ trước
        prev_revenue_stats = self.get_revenue_stats(prev_start, prev_end)
        prev_orders = self._get_period_order_count(prev_start, prev_end)
        prev_customers = self._get_period_customer_count(prev_start, prev_end)
        prev_products = self._get_period_product_count(prev_start, prev_end)

        # Tính toán số liệu kỳ hiện tại
        current_orders = self._get_period_order_count(current_start, current_end)
        current_customers = self._get_period_customer_count(current_start, current_end)
        current_products = self._get_period_product_count(current_start, current_end)

        # Tính phần trăm thay đổi
        revenue_change = self._calculate_percentage_change(
            float(time_stats['total_revenue']),
            float(prev_revenue_stats['total_revenue'])
        )
        orders_change = self._calculate_percentage_change(current_orders, prev_orders)
        customers_change = self._calculate_percentage_change(current_customers, prev_customers)
        products_change = self._calculate_percentage_change(current_products, prev_products)

        return {
            'monthly_revenue': time_stats['total_revenue'],
            'total_orders': order_stats['total'],
            'total_customers': self.get_customer_count(),
            'total_products': self.get_active_product_count(),
            'period_label': time_stats['period_label'],
            'time_stats': time_stats,
            'revenue': {
                'total_revenue': time_stats['total_revenue'],
                'order_count': time_stats['completed_orders']
            },
            'orders': order_stats,
            'sentiment': sentiment_stats,
            'promotion': promotion_stats,
            'top_products': list(self.get_top_products(5).values('name', 'sold')),
            'monthly_comparison': self.get_monthly_comparison(6),
            # Thêm các chỉ số so sánh phần trăm
            'revenue_change': revenue_change,
            'orders_change': orders_change,
            'customers_change': customers_change,
            'products_change': products_change,
            # Thêm thông tin chi tiết so sánh
            'comparison': {
                'previous_period': {
                    'start': prev_start.isoformat(),
                    'end': prev_end.isoformat(),
                    'revenue': float(prev_revenue_stats['total_revenue']),
                    'orders': prev_orders,
                    'customers': prev_customers,
                    'products': prev_products
                },
                'current_period': {
                    'start': current_start.isoformat(),
                    'end': current_end.isoformat(),
                    'orders': current_orders,
                    'customers': current_customers,
                    'products': current_products
                }
            }
        }
