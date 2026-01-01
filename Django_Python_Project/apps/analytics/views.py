"""
Analytics Views for ElectroShop
Dashboard, charts, search analytics, funnel analysis
"""
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg, Q
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from apps.orders.models import Order
from apps.products.models import Product
from apps.reviews.models import Review
from .models import DailyStats, SearchLog, FunnelEvent


# ==========================================
# 1. MAIN DASHBOARD
# ==========================================

@login_required
def analytics_dashboard(request):
    """Analytics dashboard - chỉ admin mới xem được"""
    if not request.user.is_staff:
        return render(request, '403.html', status=403)

    # Thống kê 30 ngày gần nhất
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)

    # Tổng quan
    total_orders = Order.objects.count()
    total_revenue = Order.objects.filter(status='completed').aggregate(
        total=Sum('total')
    )['total'] or 0

    total_products = Product.objects.filter(is_active=True).count()
    total_reviews = Review.objects.filter(is_approved=True).count()

    # Đơn hàng theo ngày
    daily_orders = Order.objects.filter(
        created_at__date__gte=start_date
    ).values('created_at__date').annotate(
        count=Count('id'),
        revenue=Sum('total')
    ).order_by('created_at__date')

    # Top sản phẩm bán chạy
    top_products = Product.objects.filter(
        is_active=True
    ).order_by('-sold')[:10]

    # Sentiment analysis stats
    sentiment_stats = Review.objects.filter(
        is_approved=True
    ).aggregate(
        positive=Count('id', filter=Q(sentiment='positive')),
        negative=Count('id', filter=Q(sentiment='negative')),
        neutral=Count('id', filter=Q(sentiment='neutral'))
    )

    context = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_products': total_products,
        'total_reviews': total_reviews,
        'daily_orders': list(daily_orders),
        'top_products': top_products,
        'sentiment_stats': sentiment_stats,
    }

    return render(request, 'analytics/dashboard.html', context)


# ==========================================
# 2. API ENDPOINTS
# ==========================================

@login_required
def revenue_chart_api(request):
    """API trả về dữ liệu biểu đồ doanh thu"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    days = int(request.GET.get('days', 30))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)

    daily_stats = DailyStats.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    ).order_by('date')

    data = {
        'labels': [stat.date.strftime('%Y-%m-%d') for stat in daily_stats],
        'revenue': [float(stat.total_revenue) for stat in daily_stats],
        'orders': [stat.total_orders for stat in daily_stats],
        'visitors': [stat.total_visitors for stat in daily_stats]
    }

    return JsonResponse(data)


# ==========================================
# 3. DETAILED ANALYTICS REPORTS
# ==========================================

@login_required
def search_analytics(request):
    """Thống kê tìm kiếm"""
    if not request.user.is_staff:
        return render(request, '403.html', status=403)

    # Top từ khóa tìm kiếm
    top_searches = SearchLog.objects.values('query').annotate(
        count=Count('id')
    ).order_by('-count')[:20]

    # Tìm kiếm không có kết quả
    no_results = SearchLog.objects.filter(
        results_count=0
    ).values('query').annotate(
        count=Count('id')
    ).order_by('-count')[:10]

    context = {
        'top_searches': top_searches,
        'no_results': no_results,
    }

    return render(request, 'analytics/search_analytics.html', context)


@login_required
def funnel_analytics(request):
    """Phân tích funnel conversion"""
    if not request.user.is_staff:
        return render(request, '403.html', status=403)

    # Funnel steps
    funnel_data = {}
    steps = ['view_product', 'add_to_cart', 'view_cart', 'checkout', 'complete']

    for step in steps:
        count = FunnelEvent.objects.filter(step=step).count()
        funnel_data[step] = count

    # Tính conversion rate
    conversion_rates = {}
    if funnel_data.get('view_product', 0) > 0:
        for step in steps[1:]:
            conversion_rates[step] = (
                    funnel_data[step] / funnel_data['view_product'] * 100
            )

    context = {
        'funnel_data': funnel_data,
        'conversion_rates': conversion_rates,
    }

    return render(request, 'analytics/funnel_analytics.html', context)


@login_required
def product_analytics(request):
    """Thống kê sản phẩm"""
    if not request.user.is_staff:
        return render(request, '403.html', status=403)

    # Sản phẩm có nhiều lượt xem nhất
    most_viewed = Product.objects.filter(
        is_active=True
    ).order_by('-views')[:10]

    # Sản phẩm có sentiment tốt nhất
    best_sentiment = Product.objects.filter(
        is_active=True,
        sentiment_score__gt=0
    ).order_by('-sentiment_score')[:10]

    # Sản phẩm có sentiment tệ nhất
    worst_sentiment = Product.objects.filter(
        is_active=True,
        sentiment_score__lt=0
    ).order_by('sentiment_score')[:10]

    context = {
        'most_viewed': most_viewed,
        'best_sentiment': best_sentiment,
        'worst_sentiment': worst_sentiment,
    }

    return render(request, 'analytics/product_analytics.html', context)