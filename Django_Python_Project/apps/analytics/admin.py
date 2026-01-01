from django.contrib import admin
from apps.analytics.models import FunnelEvent, SearchLog, DailyStats


@admin.register(FunnelEvent)
class FunnelEventAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'step', 'user', 'product', 'created_at']
    list_filter = ['step', 'created_at']


@admin.register(SearchLog)
class SearchLogAdmin(admin.ModelAdmin):
    list_display = ['query', 'results_count', 'user', 'clicked_product', 'created_at']
    list_filter = ['created_at']
    search_fields = ['query']


@admin.register(DailyStats)
class DailyStatsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_revenue', 'total_orders', 'total_visitors', 'conversion_rate']
    list_filter = ['date']
