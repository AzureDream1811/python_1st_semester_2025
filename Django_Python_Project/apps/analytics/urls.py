"""
Analytics URLs for ElectroShop
"""
from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.analytics_dashboard, name='dashboard'),
    path('revenue-chart/', views.revenue_chart_api, name='revenue_chart'),
    path('search/', views.search_analytics, name='search'),
    path('funnel/', views.funnel_analytics, name='funnel'),
    path('products/', views.product_analytics, name='products'),
]
