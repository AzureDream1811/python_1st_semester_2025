from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
import uuid


class Category(models.Model):
    """Model danh mục sản phẩm"""

    name = models.CharField(max_length=100, verbose_name='Tên danh mục')
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name='Mô tả')
    image = models.ImageField(
        upload_to='categories/',
        blank=True,
        null=True,
        verbose_name='Hình ảnh'
    )
    is_active = models.BooleanField(default=True, verbose_name='Đang hoạt động')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Danh mục'
        verbose_name_plural = 'Danh mục'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:category', kwargs={'slug': self.slug})

    @property
    def product_count(self):
        return self.products.filter(is_active=True).count()


class Brand(models.Model):
    """Model thương hiệu"""

    name = models.CharField(max_length=100, verbose_name='Tên thương hiệu')
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    logo = models.ImageField(
        upload_to='brands/',
        blank=True,
        null=True,
        verbose_name='Logo'
    )
    description = models.TextField(blank=True, verbose_name='Mô tả')
    is_active = models.BooleanField(default=True, verbose_name='Đang hoạt động')

    class Meta:
        verbose_name = 'Thương hiệu'
        verbose_name_plural = 'Thương hiệu'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """Model sản phẩm điện tử"""

    # Thông tin cơ bản
    name = models.CharField(max_length=255, verbose_name='Tên sản phẩm')
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    sku = models.CharField(max_length=50, unique=True, blank=True, verbose_name='Mã SKU')
    description = models.TextField(verbose_name='Mô tả')

    # Phân loại
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products',
        verbose_name='Danh mục'
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name='Thương hiệu'
    )

    # Giá cả
    price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name='Giá gốc (VNĐ)'
    )
    sale_price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        blank=True,
        null=True,
        verbose_name='Giá khuyến mãi (VNĐ)'
    )

    # Kho hàng
    stock = models.PositiveIntegerField(default=0, verbose_name='Số lượng tồn kho')

    # Hình ảnh
    image = models.ImageField(
        upload_to='products/',
        verbose_name='Hình ảnh chính'
    )

    # Thông số kỹ thuật (JSON field)
    specifications = models.JSONField(
        blank=True,
        null=True,
        verbose_name='Thông số kỹ thuật'
    )

    # Trạng thái
    is_active = models.BooleanField(default=True, verbose_name='Đang bán')
    is_featured = models.BooleanField(default=False, verbose_name='Sản phẩm nổi bật')
    is_new = models.BooleanField(default=True, verbose_name='Sản phẩm mới')

    # Thống kê
    views = models.PositiveIntegerField(default=0, verbose_name='Lượt xem')
    sold = models.PositiveIntegerField(default=0, verbose_name='Đã bán')

    # Sentiment Analysis
    sentiment_score = models.FloatField(
        default=0,
        validators=[MinValueValidator(-1), MaxValueValidator(1)],
        verbose_name='Điểm sentiment'
    )
    positive_reviews = models.PositiveIntegerField(default=0, verbose_name='Reviews tích cực')
    negative_reviews = models.PositiveIntegerField(default=0, verbose_name='Reviews tiêu cực')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')

    class Meta:
        verbose_name = 'Sản phẩm'
        verbose_name_plural = 'Sản phẩm'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.sku:
            self.sku = f"SP{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:detail', kwargs={'slug': self.slug})

    def get_active_flash_sale(self):
        """Lấy Flash Sale đang hoạt động của sản phẩm này"""
        from apps.promotions.models import FlashSale
        from django.utils import timezone
        now = timezone.now()
        return FlashSale.objects.filter(
            product=self,
            is_active=True,
            start_time__lte=now,
            end_time__gte=now,
            sold_count__lt=models.F('quantity_limit')
        ).first()

    @property
    def current_price(self):
        """Lấy giá hiện tại (giá flash sale > giá sale > giá gốc)"""
        flash_sale = self.get_active_flash_sale()
        if flash_sale:
            return flash_sale.get_effective_sale_price()
        if self.sale_price and self.sale_price < self.price:
            return self.sale_price
        return self.price

    @property
    def is_on_flash_sale(self):
        """Kiểm tra sản phẩm có đang flash sale không"""
        return self.get_active_flash_sale() is not None

    @property
    def discount_percent(self):
        """Tính % giảm giá"""
        flash_sale = self.get_active_flash_sale()
        if flash_sale:
            return flash_sale.discount_percentage
        if self.sale_price and self.sale_price < self.price:
            return int(((self.price - self.sale_price) / self.price) * 100)
        return 0

    @property
    def in_stock(self):
        """Kiểm tra còn hàng"""
        return self.stock > 0

    @property
    def average_rating(self):
        """Tính điểm đánh giá trung bình"""
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 1)
        return 0

    @property
    def review_count(self):
        """Đếm số reviews"""
        return self.reviews.filter(is_approved=True).count()

    @property
    def sentiment_label(self):
        """Nhãn sentiment dựa trên điểm"""
        if self.sentiment_score > 0.3:
            return 'positive'
        elif self.sentiment_score < -0.3:
            return 'negative'
        return 'neutral'

    def update_sentiment_stats(self):
        """Cập nhật thống kê sentiment từ reviews"""
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            positive = reviews.filter(sentiment='positive').count()
            negative = reviews.filter(sentiment='negative').count()
            total = reviews.count()

            self.positive_reviews = positive
            self.negative_reviews = negative

            if total > 0:
                self.sentiment_score = (positive - negative) / total

            self.save(update_fields=['positive_reviews', 'negative_reviews', 'sentiment_score'])


class ProductImage(models.Model):
    """Model hình ảnh sản phẩm (nhiều ảnh)"""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Sản phẩm'
    )
    image = models.ImageField(upload_to='products/', verbose_name='Hình ảnh')
    alt_text = models.CharField(max_length=255, blank=True, verbose_name='Alt text')
    is_primary = models.BooleanField(default=False, verbose_name='Ảnh chính')
    order = models.PositiveIntegerField(default=0, verbose_name='Thứ tự')

    class Meta:
        verbose_name = 'Hình ảnh sản phẩm'
        verbose_name_plural = 'Hình ảnh sản phẩm'
        ordering = ['order']

    def __str__(self):
        return f"{self.product.name} - Image {self.pk}"


class Wishlist(models.Model):
    """Model danh sách yêu thích"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wishlists',
        verbose_name='Người dùng'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='wishlisted_by',
        verbose_name='Sản phẩm'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Yêu thích'
        verbose_name_plural = 'Yêu thích'
        unique_together = ['user', 'product']

    def __str__(self):
        return f"{self.user.email} - {self.product.name}"


class FlashSale(models.Model):
    """Model cho sản phẩm Flash Sale"""

    name = models.CharField(max_length=200, verbose_name='Tên Flash Sale')
    products = models.ManyToManyField(Product, related_name='product_flash_sales', verbose_name='Sản phẩm')
    discount_percent = models.PositiveIntegerField(verbose_name='Phần trăm giảm giá')
    start_time = models.DateTimeField(verbose_name='Thời gian bắt đầu')
    end_time = models.DateTimeField(verbose_name='Thời gian kết thúc')
    is_active = models.BooleanField(default=True, verbose_name='Hoạt động')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Flash Sale'
        verbose_name_plural = 'Flash Sale'
        ordering = ['-start_time']

    def __str__(self):
        return self.name

    @property
    def is_ongoing(self):
        now = timezone.now()
        return self.is_active and self.start_time <= now <= self.end_time

    @property
    def time_remaining(self):
        if not self.is_ongoing:
            return None
        return self.end_time - timezone.now()
