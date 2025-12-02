from django.contrib import admin
from django.utils.html import format_html
from .models import Review, ReviewHelpful


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'user', 'rating_display', 'sentiment_display',
        'is_verified_purchase', 'is_approved', 'helpful_count', 'created_at'
    ]
    list_filter = ['rating', 'sentiment', 'is_approved', 'is_verified_purchase', 'created_at']
    search_fields = ['product__name', 'user__email', 'comment']
    readonly_fields = ['sentiment', 'sentiment_score', 'processed_comment', 'helpful_count']
    list_editable = ['is_approved']
    raw_id_fields = ['product', 'user', 'order_item']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('product', 'user', 'order_item', 'is_verified_purchase')
        }),
        ('Nội dung đánh giá', {
            'fields': ('rating', 'title', 'comment')
        }),
        ('Sentiment Analysis', {
            'fields': ('sentiment', 'sentiment_score', 'processed_comment'),
            'classes': ('collapse',)
        }),
        ('Hình ảnh', {
            'fields': ('image1', 'image2', 'image3'),
            'classes': ('collapse',)
        }),
        ('Trạng thái', {
            'fields': ('is_approved', 'helpful_count')
        }),
    )
    
    def rating_display(self, obj):
        stars = '⭐' * obj.rating
        return format_html('<span style="color: gold;">{}</span>', stars)
    rating_display.short_description = 'Đánh giá'
    
    def sentiment_display(self, obj):
        colors = {
            'positive': 'green',
            'negative': 'red',
            'neutral': 'gray',
        }
        labels = {
            'positive': 'Tích cực',
            'negative': 'Tiêu cực',
            'neutral': 'Trung lập',
        }
        color = colors.get(obj.sentiment, 'black')
        label = labels.get(obj.sentiment, obj.sentiment)
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} ({:.2f})</span>',
            color, label, obj.sentiment_score
        )
    sentiment_display.short_description = 'Sentiment'
    
    actions = ['approve_reviews', 'disapprove_reviews', 'reanalyze_sentiment']
    
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f'Đã duyệt {queryset.count()} đánh giá')
    approve_reviews.short_description = 'Duyệt các đánh giá đã chọn'
    
    def disapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f'Đã bỏ duyệt {queryset.count()} đánh giá')
    disapprove_reviews.short_description = 'Bỏ duyệt các đánh giá đã chọn'
    
    def reanalyze_sentiment(self, request, queryset):
        for review in queryset:
            review.sentiment = ''  # Reset để trigger analyze lại
            review.save()
        self.message_user(request, f'Đã phân tích lại sentiment cho {queryset.count()} đánh giá')
    reanalyze_sentiment.short_description = 'Phân tích lại sentiment'


@admin.register(ReviewHelpful)
class ReviewHelpfulAdmin(admin.ModelAdmin):
    list_display = ['review', 'user', 'created_at']
    list_filter = ['created_at']
    raw_id_fields = ['review', 'user']
