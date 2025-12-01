from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Brand, Product, ProductImage, Wishlist


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_active', 'product_count', 'created_at']
    list_filter = ['is_active', 'parent']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'logo_preview']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="50" height="50" />', obj.logo.url)
        return '-'
    logo_preview.short_description = 'Logo'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'brand', 'price', 'sale_price',
        'stock', 'is_active', 'is_featured', 'sentiment_display', 'created_at'
    ]
    list_filter = ['is_active', 'is_featured', 'is_new', 'category', 'brand']
    search_fields = ['name', 'sku', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'is_featured', 'stock']
    readonly_fields = ['views', 'sold', 'sentiment_score', 'positive_reviews', 'negative_reviews']
    inlines = [ProductImageInline]
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('name', 'slug', 'sku', 'description', 'short_description')
        }),
        ('Phân loại', {
            'fields': ('category', 'brand')
        }),
        ('Giá cả & Kho', {
            'fields': ('price', 'sale_price', 'stock')
        }),
        ('Hình ảnh', {
            'fields': ('image',)
        }),
        ('Thông số kỹ thuật', {
            'fields': ('specifications',),
            'classes': ('collapse',)
        }),
        ('Trạng thái', {
            'fields': ('is_active', 'is_featured', 'is_new')
        }),
        ('Thống kê', {
            'fields': ('views', 'sold', 'sentiment_score', 'positive_reviews', 'negative_reviews'),
            'classes': ('collapse',)
        }),
    )
    
    def sentiment_display(self, obj):
        score = obj.sentiment_score
        if score > 0.3:
            color = 'green'
            label = 'Tích cực'
        elif score < -0.3:
            color = 'red'
            label = 'Tiêu cực'
        else:
            color = 'gray'
            label = 'Trung lập'
        return format_html(
            '<span style="color: {};">{} ({:.2f})</span>',
            color, label, score
        )
    sentiment_display.short_description = 'Sentiment'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image_preview', 'is_primary', 'order']
    list_filter = ['is_primary']
    list_editable = ['is_primary', 'order']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return '-'
    image_preview.short_description = 'Preview'


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'product__name']
    raw_id_fields = ['user', 'product']
