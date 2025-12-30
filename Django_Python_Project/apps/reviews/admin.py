from django.contrib import admin
from django.utils.html import format_html
from .models import Review, ReviewHelpful


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Quản lý đánh giá sản phẩm với Sentiment Analysis"""
    list_display = [
        'product', 'user', 'rating_display', 'sentiment_display',
        'is_verified_purchase', 'is_approved', 'helpful_count', 'images_count', 'created_at'
    ]
    list_filter = ['rating', 'sentiment', 'is_approved', 'is_verified_purchase', 'created_at']
    search_fields = ['product__name', 'user__email', 'user__username', 'comment']
    readonly_fields = ['sentiment', 'sentiment_score', 'helpful_count', 'is_verified_purchase', 'images_preview']
    list_editable = ['is_approved']
    raw_id_fields = ['product', 'user', 'order_item']
    date_hierarchy = 'created_at'
    list_per_page = 25

    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('product', 'user', 'order_item', 'is_verified_purchase')
        }),
        ('Nội dung đánh giá', {
            'fields': ('rating', 'comment')
        }),
        ('Sentiment Analysis (FastText)', {
            'fields': ('sentiment', 'sentiment_score'),
            'classes': ('collapse',),
            'description': 'Kết quả phân tích cảm xúc từ model FastText'
        }),
        ('Hình ảnh đánh giá', {
            'fields': ('image1', 'image2', 'image3', 'images_preview'),
            'classes': ('collapse',)
        }),
        ('Trạng thái & Tương tác', {
            'fields': ('is_approved', 'helpful_count')
        }),
    )

    def rating_display(self, obj):
        """Hiển thị số sao với icon"""
        stars = '⭐' * obj.rating
        empty_stars = '☆' * (5 - obj.rating)
        return format_html('<span style="color: gold;">{}</span><span style="color: #ddd;">{}</span>', stars,
                           empty_stars)

    rating_display.short_description = 'Đánh giá'

    def sentiment_display(self, obj):
        """Hiển thị sentiment với màu sắc và icon"""
        colors = {
            'positive': ('green', '😊', 'Tích cực'),
            'negative': ('red', '😞', 'Tiêu cực'),
            'neutral': ('gray', '😐', 'Trung lập'),
        }
        color, icon, label = colors.get(obj.sentiment, ('black', '❓', obj.sentiment or 'N/A'))
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {} ({:.2f})</span>',
            color, icon, label, obj.sentiment_score
        )

    sentiment_display.short_description = 'Sentiment'

    def images_count(self, obj):
        """Đếm số hình ảnh"""
        count = len(obj.get_images())
        if count > 0:
            return format_html('<span style="color: blue;">📷 {}</span>', count)
        return '-'

    images_count.short_description = 'Ảnh'

    def images_preview(self, obj):
        """Hiển thị preview hình ảnh"""
        images = obj.get_images()
        if not images:
            return 'Không có hình ảnh'
        html = ''
        for img in images:
            html += f'<img src="{img.url}" width="100" height="100" style="object-fit: cover; margin-right: 10px; border-radius: 5px;" />'
        return format_html(html)

    images_preview.short_description = 'Preview hình ảnh'

    actions = ['approve_reviews', 'disapprove_reviews', 'reanalyze_sentiment', 'mark_verified']

    def approve_reviews(self, request, queryset):
        """Duyệt các đánh giá đã chọn"""
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'✅ Đã duyệt {updated} đánh giá')

    approve_reviews.short_description = '✅ Duyệt các đánh giá đã chọn'

    def disapprove_reviews(self, request, queryset):
        """Bỏ duyệt các đánh giá đã chọn"""
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'❌ Đã bỏ duyệt {updated} đánh giá')

    disapprove_reviews.short_description = '❌ Bỏ duyệt các đánh giá đã chọn'

    def reanalyze_sentiment(self, request, queryset):
        """Phân tích lại sentiment bằng FastText"""
        count = 0
        for review in queryset:
            if review.comment:
                review.sentiment = ''  # Reset để trigger analyze lại
                review.save()
                count += 1
        self.message_user(request, f'🔄 Đã phân tích lại sentiment cho {count} đánh giá')

    reanalyze_sentiment.short_description = '🔄 Phân tích lại sentiment (FastText)'

    def mark_verified(self, request, queryset):
        """Đánh dấu là mua hàng xác thực"""
        updated = queryset.update(is_verified_purchase=True)
        self.message_user(request, f'✓ Đã đánh dấu {updated} đánh giá là mua hàng xác thực')

    mark_verified.short_description = '✓ Đánh dấu mua hàng xác thực'


@admin.register(ReviewHelpful)
class ReviewHelpfulAdmin(admin.ModelAdmin):
    """Quản lý lượt đánh giá hữu ích"""
    list_display = ['review_info', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['review__product__name', 'user__email', 'user__username']
    raw_id_fields = ['review', 'user']
    list_per_page = 25
    date_hierarchy = 'created_at'

    def review_info(self, obj):
        """Hiển thị thông tin review"""
        return format_html(
            'Review #{} - {} ({}⭐)',
            obj.review.pk, obj.review.product.name[:30], obj.review.rating
        )

    review_info.short_description = 'Đánh giá'
