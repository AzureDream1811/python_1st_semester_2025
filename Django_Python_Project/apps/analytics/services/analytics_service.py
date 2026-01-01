from django.db.models import Sum, Count, Avg, F
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal


class AnalyticsService:
    """Service for analytics and reporting"""

    @staticmethod
    def get_revenue_data(start_date=None, end_date=None, group_by='day'):
        """Get revenue data with optional date range and grouping"""
        from apps.orders.models import Order

        if not start_date:
            start_date = timezone.now() - timedelta(days=30)
        if not end_date:
            end_date = timezone.now()

        orders = Order.objects.filter(
            created_at__range=[start_date, end_date],
            status__in=['completed', 'delivered']
        )

        if group_by == 'day':
            data = orders.annotate(
                date=TruncDate('created_at')
            ).values('date').annotate(
                revenue=Sum('total'),
                orders=Count('id')
            ).order_by('date')
        elif group_by == 'month':
            data = orders.annotate(
                date=TruncMonth('created_at')
            ).values('date').annotate(
                revenue=Sum('total'),
                orders=Count('id')
            ).order_by('date')
        else:
            data = [{
                'revenue': orders.aggregate(Sum('total'))['total__sum'] or 0,
                'orders': orders.count()
            }]

        return list(data)

    @staticmethod
    def get_rfm_analysis():
        """RFM (Recency, Frequency, Monetary) analysis for customer segmentation"""
        from apps.orders.models import Order
        from django.contrib.auth import get_user_model
        User = get_user_model()

        now = timezone.now()

        # Get customer metrics
        customers = User.objects.filter(
            orders__status__in=['completed', 'delivered']
        ).annotate(
            last_order=Max('orders__created_at'),
            order_count=Count('orders'),
            total_spent=Sum('orders__total')
        ).values('id', 'username', 'email', 'last_order', 'order_count', 'total_spent')

        rfm_data = []
        for customer in customers:
            if customer['last_order']:
                recency = (now - customer['last_order']).days
            else:
                recency = 999

            # Score calculation (1-5)
            r_score = 5 if recency <= 30 else 4 if recency <= 60 else 3 if recency <= 90 else 2 if recency <= 180 else 1
            f_score = 5 if customer['order_count'] >= 10 else 4 if customer['order_count'] >= 5 else 3 if customer[
                                                                                                              'order_count'] >= 3 else 2 if \
                customer['order_count'] >= 2 else 1
            m_score = 5 if customer['total_spent'] >= 10000000 else 4 if customer['total_spent'] >= 5000000 else 3 if \
                customer['total_spent'] >= 2000000 else 2 if customer['total_spent'] >= 500000 else 1

            # Segment
            rfm_score = r_score * 100 + f_score * 10 + m_score
            if rfm_score >= 444:
                segment = 'Champions'
            elif rfm_score >= 334:
                segment = 'Loyal Customers'
            elif rfm_score >= 311:
                segment = 'Potential Loyalists'
            elif r_score >= 4:
                segment = 'New Customers'
            elif r_score <= 2 and f_score <= 2:
                segment = 'At Risk'
            else:
                segment = 'Need Attention'

            rfm_data.append({
                'customer': customer,
                'recency': recency,
                'frequency': customer['order_count'],
                'monetary': customer['total_spent'],
                'r_score': r_score,
                'f_score': f_score,
                'm_score': m_score,
                'segment': segment
            })

        return rfm_data

    @staticmethod
    def forecast_revenue(days=30):
        """Simple revenue forecast using moving average"""
        from apps.orders.models import Order

        # Get historical data
        end_date = timezone.now()
        start_date = end_date - timedelta(days=90)

        daily_revenue = Order.objects.filter(
            created_at__range=[start_date, end_date],
            status__in=['completed', 'delivered']
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            revenue=Sum('total')
        ).order_by('date')

        revenues = [d['revenue'] or 0 for d in daily_revenue]

        if len(revenues) < 7:
            return []

        # Simple moving average forecast
        window = 7
        forecast = []
        for i in range(days):
            if len(revenues) >= window:
                avg = sum(revenues[-window:]) / window
            else:
                avg = sum(revenues) / len(revenues) if revenues else 0

            forecast.append({
                'date': end_date + timedelta(days=i + 1),
                'predicted_revenue': float(avg)
            })
            revenues.append(avg)

        return forecast

    @staticmethod
    def get_conversion_rate(start_date=None, end_date=None):
        """Calculate conversion rate (views to purchases)"""
        from apps.analytics.models import FunnelEvent

        if not start_date:
            start_date = timezone.now() - timedelta(days=30)
        if not end_date:
            end_date = timezone.now()

        events = FunnelEvent.objects.filter(
            created_at__range=[start_date, end_date]
        )

        views = events.filter(event_type='view').count()
        purchases = events.filter(event_type='purchase').count()

        conversion_rate = (purchases / views * 100) if views > 0 else 0

        return {
            'views': views,
            'purchases': purchases,
            'conversion_rate': round(conversion_rate, 2)
        }

    @staticmethod
    def get_funnel_data(start_date=None, end_date=None):
        """Get conversion funnel data"""
        from apps.analytics.models import FunnelEvent

        if not start_date:
            start_date = timezone.now() - timedelta(days=30)
        if not end_date:
            end_date = timezone.now()

        events = FunnelEvent.objects.filter(
            created_at__range=[start_date, end_date]
        )

        funnel = {
            'view': events.filter(event_type='view').count(),
            'add_to_cart': events.filter(event_type='add_to_cart').count(),
            'checkout': events.filter(event_type='checkout').count(),
            'purchase': events.filter(event_type='purchase').count(),
        }

        # Calculate rates
        if funnel['view'] > 0:
            funnel['cart_rate'] = round(funnel['add_to_cart'] / funnel['view'] * 100, 2)
            funnel['checkout_rate'] = round(funnel['checkout'] / funnel['view'] * 100, 2)
            funnel['purchase_rate'] = round(funnel['purchase'] / funnel['view'] * 100, 2)
        else:
            funnel['cart_rate'] = funnel['checkout_rate'] = funnel['purchase_rate'] = 0

        return funnel

    @staticmethod
    def export_report(report_type, start_date, end_date, format='pdf'):
        """Export report to PDF or Excel"""
        if format == 'pdf':
            return AnalyticsService._export_pdf(report_type, start_date, end_date)
        else:
            return AnalyticsService._export_excel(report_type, start_date, end_date)

    @staticmethod
    def _export_pdf(report_type, start_date, end_date):
        """Generate PDF report"""
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
        from io import BytesIO

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # Title
        elements.append(Paragraph(f'Báo cáo {report_type}', styles['Heading1']))
        elements.append(Paragraph(f'Từ {start_date} đến {end_date}', styles['Normal']))

        # Get data based on report type
        if report_type == 'revenue':
            data = AnalyticsService.get_revenue_data(start_date, end_date)
            table_data = [['Ngày', 'Doanh thu', 'Số đơn']]
            for row in data:
                table_data.append([
                    str(row['date']),
                    f"{row['revenue']:,.0f}đ",
                    str(row['orders'])
                ])

        if table_data:
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(table)

        doc.build(elements)
        buffer.seek(0)
        return buffer

    @staticmethod
    def _export_excel(report_type, start_date, end_date):
        """Generate Excel report"""
        import openpyxl
        from io import BytesIO

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = report_type

        # Get data based on report type
        if report_type == 'revenue':
            data = AnalyticsService.get_revenue_data(start_date, end_date)
            ws.append(['Ngày', 'Doanh thu', 'Số đơn'])
            for row in data:
                ws.append([str(row['date']), row['revenue'], row['orders']])

        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer
