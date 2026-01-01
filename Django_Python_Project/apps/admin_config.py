"""
Custom Admin Site Configuration
Tùy chỉnh giao diện và cấu hình cho Django Admin
"""
from django.contrib import admin
from django.contrib.admin import AdminSite


class ShopAdminSite(AdminSite):
    """Custom Admin Site cho Admin"""

    # Tiêu đề hiển thị trên trang admin
    site_header = "🔌Shop Admin"

    # Tiêu đề trên tab trình duyệt
    site_title = "AdminShop"

    # Tiêu đề trên trang index
    index_title = "Quản trị hệ thống bán hàng điện gia dụng"

    def index(self, request, extra_context=None):
        """Override index để thêm dashboard statistics"""
        extra_context = extra_context or {}

        try:
            from apps.admin_dashboard.services.statistics import DashboardStatistics
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


# Cấu hình admin site mặc định
admin.site.site_header = "🔌Shop Admin"
admin.site.site_title = "Admin Shop"
admin.site.index_title = "Quản trị hệ thống bán hàng điện gia dụng"

# Override index method của default admin site
original_index = admin.site.index


def custom_index(request, extra_context=None):
    """Custom index với dashboard statistics"""
    extra_context = extra_context or {}

    try:
        from apps.admin_dashboard.services.statistics import DashboardStatistics
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

    return original_index(request, extra_context)


admin.site.index = custom_index
