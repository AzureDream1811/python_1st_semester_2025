from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from datetime import datetime, timedelta

from .services.statistics import DashboardStatistics


@method_decorator(staff_member_required, name='dispatch')
class RevenueReportPageView(TemplateView):
    """Trang báo cáo doanh thu"""
    template_name = 'admin/revenue_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.now().date()
        context['end_date'] = today.isoformat()
        context['start_date'] = (today - timedelta(days=30)).isoformat()
        return context


@method_decorator(staff_member_required, name='dispatch')
class ChartDataView(View):
    """API endpoint cung cấp dữ liệu cho biểu đồ"""
    
    def get(self, request):
        chart_type = request.GET.get('type', 'revenue')
        stats = DashboardStatistics()
        
        if chart_type == 'revenue':
            return JsonResponse(stats.get_daily_revenue_chart_data())
        elif chart_type == 'orders':
            return JsonResponse(stats.get_order_status_chart_data())
        elif chart_type == 'sentiment':
            return JsonResponse(stats.get_sentiment_chart_data())
        elif chart_type == 'category':
            return JsonResponse(stats.get_category_revenue_chart_data())
        
        return JsonResponse({'error': 'Invalid chart type'}, status=400)


@method_decorator(staff_member_required, name='dispatch')
class RevenueReportView(View):
    """API endpoint cho báo cáo doanh thu"""
    
    def get(self, request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        stats = DashboardStatistics()
        
        if start_date and end_date:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            end = datetime.now().date()
            start = end - timedelta(days=30)
        
        report = stats.get_revenue_report(start, end)
        return JsonResponse(report)
