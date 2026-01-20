from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from typing import TYPE_CHECKING, Tuple, Dict
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

    if TYPE_CHECKING:
        # Help static type checkers know that `Review` has a related manager `helpful_votes`
        from django.db.models.manager import Manager

        helpful_votes: 'Manager["ReviewHelpful"]'

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
        """
        Phân tích sentiment cho review.

        Kết hợp text sentiment với star rating sử dụng weighted average:
        - Text sentiment chiếm 60%
        - Star rating chiếm 40%

        Điều này giúp:
        - Giảm thiểu mâu thuẫn giữa nội dung và số sao
        - Tạo ra sentiment score phản ánh cả hai yếu tố
        """
        from .sentiment import SentimentAnalyzer

        analyzer = SentimentAnalyzer()
        # Truyền cả comment và rating để kết hợp
        result = analyzer.analyze(self.comment, rating=self.rating)

        self.sentiment = result['sentiment']
        self.sentiment_score = result['score']
        # text_score và rating_score có thể được log/debug nếu cần

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

    @property
    def rating_sentiment_mismatch(self):
        """
        Kiểm tra xem số sao có khớp với sentiment không
        
        Returns:
            dict: {'mismatch': bool, 'message': str, 'severity': str}
            
        Logic:
        - 4-5 sao nhưng sentiment tiêu cực → mismatch nghiêm trọng
        - 1-2 sao nhưng sentiment tích cực → mismatch nghiêm trọng  
        - 3 sao với sentiment mạnh → mismatch nhẹ
        """
        if not self.sentiment:
            return {'mismatch': False, 'message': '', 'severity': 'none'}

        if self.rating >= 4 and self.sentiment == 'negative':
            return {
                'mismatch': True,
                'message': f'Cảnh báo: Đánh giá {self.rating} sao nhưng nội dung tiêu cực (AI score: {self.sentiment_score:.2f})',
                'severity': 'high'
            }

        if self.rating <= 2 and self.sentiment == 'positive':
            return {
                'mismatch': True,
                'message': f'Cảnh báo: Đánh giá {self.rating} sao nhưng nội dung tích cực (AI score: {self.sentiment_score:.2f})',
                'severity': 'high'
            }

        if self.rating == 3:
            if self.sentiment == 'positive' and self.sentiment_score > 0.7:
                return {
                    'mismatch': True,
                    'message': 'Gợi ý: Nội dung rất tích cực, có thể xem xét nâng sao',
                    'severity': 'low'
                }
            if self.sentiment == 'negative' and self.sentiment_score < -0.7:
                return {
                    'mismatch': True,
                    'message': 'Gợi ý: Nội dung tiêu cực mạnh, có thể xem xét giảm sao',
                    'severity': 'low'
                }

        return {'mismatch': False, 'message': '', 'severity': 'none'}

    @property
    def ai_suggested_rating(self):
        """
        Gợi ý số sao dựa trên phân tích AI
        
        Returns:
            int: Số sao được gợi ý (1-5)
        """
        if not self.sentiment or self.sentiment_score == 0:
            return self.rating

        if self.sentiment_score >= 0.8:
            return 5
        elif self.sentiment_score >= 0.5:
            return 4
        elif self.sentiment_score >= -0.2:
            return 3
        elif self.sentiment_score >= -0.6:
            return 2
        else:
            return 1


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
        result: Tuple[int, Dict[str, int]] = super().delete(*args, **kwargs)
        # Cập nhật số lượt hữu ích
        review.helpful_count = review.helpful_votes.count()
        review.save(update_fields=['helpful_count'])
        return result
