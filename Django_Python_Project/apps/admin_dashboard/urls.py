from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('api/chart-data/', views.ChartDataView.as_view(), name='chart_data'),
    path('api/revenue-report/', views.RevenueReportView.as_view(), name='revenue_report_api'),
    path('revenue-report/', views.RevenueReportPageView.as_view(), name='revenue_report'),
]
