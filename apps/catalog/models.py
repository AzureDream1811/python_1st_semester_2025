from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator


class CategoryManager(models.Manager):
    """Custom manager cho Category"""

    def active(self):
        """Lấy các danh mục đang hoạt động"""
        return self.filter(is_active=True)

    def root_categories(self):
        """Lấy các danh mục gốc (không có parent)"""
        return self.filter(parent__isnull=True, is_active=True)


class Category(models.Model):
    """Model danh mục sản phẩm với cấu trúc cây"""

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Tên danh mục'
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        verbose_name='Slug URL'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Mô tả'
    )
    image = models.ImageField(
        upload_to='catalog/categories/',
        blank=True,
        null=True,
        verbose_name='Hình ảnh danh mục'
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text='CSS class cho icon (VD: fa-laptop, fa-mobile)',
        verbose_name='Icon CSS Class'
    )

    # Cấu trúc cây (parent-child)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Danh mục cha'
    )

    # Sắp xếp và hiển thị
    order = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Thứ tự hiển thị'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Đang hoạt động'
    )

    # Metadata
    meta_title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Meta Title (SEO)'
    )
    meta_description = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='Meta Description (SEO)'
    )
    meta_keywords = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Meta Keywords (SEO)'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CategoryManager()

    class Meta:
        verbose_name = 'Danh mục'
        verbose_name_plural = 'Danh mục sản phẩm'
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'order']),
        ]

    def __str__(self):
        return self.get_full_path()

    def save(self, *args, **kwargs):
        """Tự động tạo slug từ name nếu chưa có"""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """URL để xem danh mục"""
        return reverse('catalog:category_detail', kwargs={'slug': self.slug})

    def get_full_path(self):
        """Lấy đường dẫn đầy đủ của danh mục (Parent > Child)"""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name

    def get_all_children(self):
        """Lấy tất cả danh mục con (recursive)"""
        children = list(self.children.filter(is_active=True))
        for child in list(children):
            children.extend(child.get_all_children())
        return children

    def get_products_count(self):
        """Đếm số lượng sản phẩm trong danh mục"""
        from apps.products.models import Product
        return Product.objects.filter(
            category=self,
            is_active=True
        ).count()

    def get_all_products_count(self):
        """Đếm tổng số sản phẩm bao gồm cả danh mục con"""
        from apps.products.models import Product
        categories = [self] + self.get_all_children()
        return Product.objects.filter(
            category__in=categories,
            is_active=True
        ).count()

    @property
    def level(self):
        """Tính cấp độ của danh mục trong cây"""
        if self.parent is None:
            return 0
        return 1 + self.parent.level

    @property
    def is_root(self):
        """Kiểm tra có phải danh mục gốc không"""
        return self.parent is None

    @property
    def has_children(self):
        """Kiểm tra có danh mục con không"""
        return self.children.exists()


class Tag(models.Model):
    """Model cho tags/nhãn sản phẩm"""

    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Tên tag'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        blank=True,
        verbose_name='Slug URL'
    )
    color = models.CharField(
        max_length=7,
        default='#007bff',
        help_text='Mã màu HEX (VD: #FF5733)',
        verbose_name='Màu hiển thị'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Mô tả'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Đang hoạt động'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Tự động tạo slug từ name"""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """URL để xem sản phẩm theo tag"""
        return reverse('catalog:tag_detail', kwargs={'slug': self.slug})

    def get_products_count(self):
        """Đếm số lượng sản phẩm có tag này"""
        return self.products.filter(is_active=True).count()

