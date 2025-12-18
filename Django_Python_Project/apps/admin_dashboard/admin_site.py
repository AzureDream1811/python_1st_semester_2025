"""
Custom Admin Site cho ElectroShop
Tùy chỉnh giao diện và thêm dashboard statistics
"""
from django.contrib.admin import AdminSite
from django.urls import path
from .services.statistics import DashboardStatistics


class ElectroShopAdminSite(AdminSite):
    """Custom Admin Site với dashboard thống kê"""
    
    site_header = "🔌 ElectroShop Admin"
    site_title = "ElectroShop"
    index_title = "Quản trị hệ thống bán hàng điện gia dụng"
    
    def index(self, request, extra_context=None):
        """Override index để thêm dashboard statistics"""
        extra_context = extra_context or {}
        
        try:
            stats = DashboardStatistics()
            dashboard_data = stats.get_dashboard_summary()
            extra_context.update({
                'dashboard_stats': dashboard_data,
                'has_dashboard': True
            })
        except Exception as e:
            extra_context.update({
                'dashboard_error': str(e),
                'has_dashboard': False
            })
        
        return super().index(request, extra_context)
    
    def get_urls(self):
        """Thêm custom URLs cho dashboard"""
        from . import views
        
        urls = super().get_urls()
        custom_urls = [
            path('api/chart-data/', 
                 self.admin_view(views.ChartDataView.as_view()), 
                 name='chart_data'),
            path('api/revenue-report/', 
                 self.admin_view(views.RevenueReportView.as_view()), 
                 name='revenue_report'),
        ]
        return custom_urls + urls


# Instance của custom admin site
electroshop_admin = ElectroShopAdminSite(name='electroshop_admin')
