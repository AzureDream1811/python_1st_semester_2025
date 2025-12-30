from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Brand, Product, ProductImage, Wishlist, FlashSale


class ProductImageInline(admin.TabularInline):
    """Inline hiển thị hình ảnh sản phẩm"""
    model = ProductImage
    extra = 1
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="80" height="80" style="object-fit: cover;" />', obj.image.url)
        return '-'

    image_preview.short_description = 'Preview'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Quản lý danh mục sản phẩm"""
    list_display = ['name', 'slug', 'is_active', 'product_count', 'image_preview', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']
    list_per_page = 25

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />',
                               obj.image.url)
        return '-'

    image_preview.short_description = 'Hình ảnh'


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """Quản lý thương hiệu"""
    list_display = ['name', 'slug', 'is_active', 'logo_preview']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']
    list_per_page = 25

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: contain;" />', obj.logo.url)
        return '-'

    logo_preview.short_description = 'Logo'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Quản lý sản phẩm điện gia dụng"""
    list_display = [
        'name', 'sku', 'category', 'brand', 'price_display', 'sale_price_display',
        'stock', 'is_active', 'is_featured', 'sentiment_display', 'sold', 'created_at'
    ]
    list_filter = ['is_active', 'is_featured', 'is_new', 'category', 'brand', 'created_at']
    search_fields = ['name', 'sku', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'is_featured', 'stock']
    readonly_fields = ['views', 'sold', 'sentiment_score', 'positive_reviews', 'negative_reviews', 'sku',
                       'image_preview']
    inlines = [ProductImageInline]
    list_per_page = 25
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('name', 'slug', 'sku', 'description')
        }),
        ('Phân loại', {
            'fields': ('category', 'brand')
        }),
        ('Giá cả & Kho', {
            'fields': ('price', 'sale_price', 'stock')
        }),
        ('Hình ảnh', {
            'fields': ('image', 'image_preview')
        }),
        ('Thông số kỹ thuật', {
            'fields': ('specifications',),
            'classes': ('collapse',)
        }),
        ('Trạng thái', {
            'fields': ('is_active', 'is_featured', 'is_new')
        }),
        ('Thống kê & Sentiment', {
            'fields': ('views', 'sold', 'sentiment_score', 'positive_reviews', 'negative_reviews'),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        """Hiển thị ảnh preview"""
        if obj.image:
            return format_html('<img src="{}" width="150" height="150" style="object-fit: contain;" />', obj.image.url)
        return '-'

    image_preview.short_description = 'Preview'

    def price_display(self, obj):
        """Hiển thị giá gốc với format VND"""
        return f"{obj.price:,.0f}đ"

    price_display.short_description = 'Giá gốc'

    def sale_price_display(self, obj):
        """Hiển thị giá sale với format VND"""
        if obj.sale_price:
            discount = obj.discount_percent
            return format_html(
                '<span style="color: red;">{:,.0f}đ</span> <small>(-{}%)</small>',
                obj.sale_price, discount
            )
        return '-'

    sale_price_display.short_description = 'Giá KM'

    def sentiment_display(self, obj):
        """Hiển thị sentiment với màu sắc"""
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

    actions = ['make_featured', 'remove_featured', 'activate_products', 'deactivate_products']

    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f'Đã đánh dấu {queryset.count()} sản phẩm là nổi bật')

    make_featured.short_description = 'Đánh dấu là sản phẩm nổi bật'

    def remove_featured(self, request, queryset):
        queryset.update(is_featured=False)
        self.message_user(request, f'Đã bỏ đánh dấu nổi bật {queryset.count()} sản phẩm')

    remove_featured.short_description = 'Bỏ đánh dấu nổi bật'

    def activate_products(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'Đã kích hoạt {queryset.count()} sản phẩm')

    activate_products.short_description = 'Kích hoạt sản phẩm'

    def deactivate_products(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'Đã vô hiệu hóa {queryset.count()} sản phẩm')

    deactivate_products.short_description = 'Vô hiệu hóa sản phẩm'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Quản lý hình ảnh sản phẩm"""
    list_display = ['product', 'image_preview', 'alt_text', 'is_primary', 'order']
    list_filter = ['is_primary', 'product__category']
    search_fields = ['product__name', 'alt_text']
    list_editable = ['is_primary', 'order']
    raw_id_fields = ['product']
    list_per_page = 25

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="60" height="60" style="object-fit: cover;" />', obj.image.url)
        return '-'

    image_preview.short_description = 'Preview'


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    """Quản lý danh sách yêu thích"""
    list_display = ['user', 'product', 'product_price', 'created_at']
    list_filter = ['created_at', 'product__category']
    search_fields = ['user__username', 'user__email', 'product__name']
    raw_id_fields = ['user', 'product']
    list_per_page = 25
    date_hierarchy = 'created_at'

    def product_price(self, obj):
        """Hiển thị giá sản phẩm"""
        return f"{obj.product.current_price:,.0f}đ"

    product_price.short_description = 'Giá hiện tại'


@admin.register(FlashSale)
class FlashSaleAdmin(admin.ModelAdmin):
    """Quản lý Flash Sale"""
    list_display = ['name', 'discount_percent', 'start_time', 'end_time', 'is_active', 'status_display',
                    'product_count']
    list_filter = ['is_active', 'start_time', 'end_time']
    search_fields = ['name']
    filter_horizontal = ['products']
    list_editable = ['is_active', 'discount_percent']
    list_per_page = 25

    fieldsets = (
        ('Thông tin Flash Sale', {
            'fields': ('name', 'discount_percent', 'is_active')
        }),
        ('Thời gian', {
            'fields': ('start_time', 'end_time')
        }),
        ('Sản phẩm', {
            'fields': ('products',)
        }),
    )

    def status_display(self, obj):
        """Hiển thị trạng thái Flash Sale"""
        if obj.is_ongoing:
            return format_html('<span style="color: green; font-weight: bold;">🔥 Đang diễn ra</span>')
        elif obj.is_active:
            return format_html('<span style="color: orange;">⏳ Chờ bắt đầu</span>')
        return format_html('<span style="color: gray;">Đã kết thúc</span>')

    status_display.short_description = 'Trạng thái'

    def product_count(self, obj):
        """Đếm số sản phẩm trong Flash Sale"""
        return obj.products.count()

    product_count.short_description = 'Số SP'
