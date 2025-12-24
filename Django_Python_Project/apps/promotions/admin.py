from django.contrib import admin
from apps.promotions.models import Voucher, VoucherUsage, ComboDeal, FlashSale


@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'discount_type', 'discount_value', 'used_count', 'usage_limit', 'is_active', 'valid_until']
    list_filter = ['discount_type', 'is_active', 'valid_from', 'valid_until']
    search_fields = ['code', 'name']


@admin.register(VoucherUsage)
class VoucherUsageAdmin(admin.ModelAdmin):
    list_display = ['voucher', 'user', 'order', 'discount_amount', 'used_at']
    list_filter = ['used_at']


@admin.register(ComboDeal)
class ComboDealAdmin(admin.ModelAdmin):
    list_display = ['name', 'discount_type', 'discount_value', 'is_active', 'valid_until']
    list_filter = ['is_active', 'discount_type']
    filter_horizontal = ['products']


@admin.register(FlashSale)
class FlashSaleAdmin(admin.ModelAdmin):
    list_display = ['product', 'sale_price', 'sold_count', 'quantity_limit', 'start_time', 'end_time', 'is_active']
    list_filter = ['is_active', 'start_time']
