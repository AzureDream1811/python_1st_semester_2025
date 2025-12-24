from django.contrib import admin
from apps.recommendations.models import UserActivity, ProductSimilarity, FrequentlyBoughtTogether


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'product', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['user__username', 'product__name']


@admin.register(ProductSimilarity)
class ProductSimilarityAdmin(admin.ModelAdmin):
    list_display = ['product', 'similar_product', 'score', 'updated_at']
    search_fields = ['product__name', 'similar_product__name']


@admin.register(FrequentlyBoughtTogether)
class FrequentlyBoughtTogetherAdmin(admin.ModelAdmin):
    list_display = ['product', 'related_product', 'count', 'updated_at']
    search_fields = ['product__name', 'related_product__name']
