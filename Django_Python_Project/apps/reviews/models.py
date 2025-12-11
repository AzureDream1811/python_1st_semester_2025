from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.products.models import Product
from apps.orders.models import OrderItem


class Review(models.Model):
    """Model đánh giá sản phẩm với sentiment analysis"""
    
    SENTIMENT_CHOICES = [
        ('positive', 'Tích cực'),
        ('negative', 'Tiêu cực'),
        ('neutral', 'Trung lập'),
    ]
    
    RATING_CHOICES = [
        (1, '1 sao'),
        (2, '2 sao'),
        (3, '3 sao'),
        (4, '4 sao'),
        (5, '5 sao'),
    ]
    
    # Liên kết
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Sản phẩm'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Người đánh giá'
    )
    order_item = models.OneToOneField(
        OrderItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='review',
        verbose_name='Sản phẩm đã mua'
    )
    
    # Nội dung đánh giá
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Đánh giá sao'
    )
    comment = models.TextField(verbose_name='Nội dung đánh giá')
    
    # Sentiment Analysis
    sentiment = models.CharField(
        max_length=10,
        choices=SENTIMENT_CHOICES,
        blank=True,
        verbose_name='Cảm xúc'
    )
    sentiment_score = models.FloatField(
        default=0,
        validators=[MinValueValidator(-1), MaxValueValidator(1)],
        verbose_name='Điểm sentiment'
    )
    
    # Hình ảnh đánh giá
    image1 = models.ImageField(
        upload_to='reviews/',
        blank=True,
        null=True,
        verbose_name='Hình ảnh 1'
    )
    image2 = models.ImageField(
        upload_to='reviews/',
        blank=True,
        null=True,
        verbose_name='Hình ảnh 2'
    )
    image3 = models.ImageField(
        upload_to='reviews/',
        blank=True,
        null=True,
        verbose_name='Hình ảnh 3'
    )
    
    # Trạng thái
    is_approved = models.BooleanField(default=True, verbose_name='Đã duyệt')
    is_verified_purchase = models.BooleanField(
        default=False,
        verbose_name='Mua hàng xác thực'
    )
    
    # Tương tác
    helpful_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Lượt hữu ích'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')
    
    class Meta:
        verbose_name = 'Đánh giá'
        verbose_name_plural = 'Đánh giá'
        ordering = ['-created_at']
        unique_together = ['product', 'user', 'order_item']
    
    def __str__(self):
        return f"{self.user.email} - {self.product.name} ({self.rating} sao)"
    
    def save(self, *args, **kwargs):
        # Kiểm tra verified purchase
        if self.order_item:
            self.is_verified_purchase = True
        
        # Xử lý sentiment nếu có comment
        if self.comment and not self.sentiment:
            self.analyze_sentiment()
        
        super().save(*args, **kwargs)
        
        # Cập nhật sentiment cho sản phẩm
        self.product.update_sentiment_stats()
    
    def analyze_sentiment(self):
        """Phân tích sentiment cho review"""
        from .sentiment import SentimentAnalyzer
        
        analyzer = SentimentAnalyzer()
        result = analyzer.analyze(self.comment)
        
        self.sentiment = result['sentiment']
        self.sentiment_score = result['score']
        self.processed_comment = result['processed_text']
    
    def get_images(self):
        """Lấy danh sách hình ảnh"""
        images = []
        for img in [self.image1, self.image2, self.image3]:
            if img:
                images.append(img)
        return images
    
    @property
    def sentiment_color(self):
        """Màu hiển thị sentiment"""
        colors = {
            'positive': 'success',
            'negative': 'danger',
            'neutral': 'secondary',
        }
        return colors.get(self.sentiment, 'secondary')


class ReviewHelpful(models.Model):
    """Model đánh dấu review hữu ích"""
    
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='helpful_votes',
        verbose_name='Đánh giá'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='helpful_votes',
        verbose_name='Người dùng'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Phiếu hữu ích'
        verbose_name_plural = 'Phiếu hữu ích'
        unique_together = ['review', 'user']
    
    def __str__(self):
        return f"{self.user.email} - Review #{self.review.pk}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Cập nhật số lượt hữu ích
        self.review.helpful_count = self.review.helpful_votes.count()
        self.review.save(update_fields=['helpful_count'])
    
    def delete(self, *args, **kwargs):
        review = self.review
        super().delete(*args, **kwargs)
        # Cập nhật số lượt hữu ích
        review.helpful_count = review.helpful_votes.count()
        review.save(update_fields=['helpful_count'])
