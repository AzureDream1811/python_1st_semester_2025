"""
Forms cho Admin Dashboard
"""
from django import forms
from django.contrib.auth.models import User
from apps.products.models import Product, Category, Brand
from apps.orders.models import Order
from apps.promotions.models import Voucher, FlashSale, ComboDeal
from apps.notifications.models import Notification


class ProductForm(forms.ModelForm):
    """Form tạo/sửa sản phẩm với validation đầy đủ"""

    ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp']
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
    MAX_FEATURED_PRODUCTS = 20

    class Meta:
        model = Product
        fields = [
            'name', 'slug', 'sku', 'description', 'category', 'brand',
            'price', 'sale_price', 'stock', 'image', 'specifications',
            'is_active', 'is_featured', 'is_new'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: iPhone 15 Pro Max 256GB'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tự động tạo nếu để trống'}),
            'sku': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'VD: IP15PM256-BLK (tự động tạo nếu để trống)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5,
                                                 'placeholder': 'Mô tả chi tiết sản phẩm (tối thiểu 20 ký tự)'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'brand': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(
                attrs={'class': 'form-control', 'min': '1000', 'step': '1000', 'placeholder': 'VD: 25000000'}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '1000',
                                                   'placeholder': 'Để trống nếu không khuyến mãi'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': '0'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': '.jpg,.jpeg,.png,.webp'}),
            'specifications': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3, 'placeholder': '{"RAM": "8GB", "Storage": "256GB"}'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_new': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
        self.fields['brand'].queryset = Brand.objects.filter(is_active=True)
        self.fields['category'].empty_label = "-- Chọn danh mục --"
        self.fields['brand'].empty_label = "-- Chọn thương hiệu (tùy chọn) --"
        self.fields['brand'].required = False
        self.warnings = []

    def clean_name(self):
        """Validation tên sản phẩm"""
        import re
        name = self.cleaned_data.get('name', '').strip()

        if not name:
            raise forms.ValidationError('Tên sản phẩm không được để trống.')

        name = ' '.join(name.split())

        if len(name) < 5:
            raise forms.ValidationError('Tên sản phẩm phải có ít nhất 5 ký tự.')

        if len(name) > 200:
            raise forms.ValidationError('Tên sản phẩm không được quá 200 ký tự.')

        if not re.match(r"^[\w\s\-&/\u00C0-\u1EF9]+$", name, re.UNICODE):
            raise forms.ValidationError('Tên sản phẩm chỉ được chứa chữ cái, số, khoảng trắng, dấu gạch ngang, & và /.')

        return name

    def clean_slug(self):
        """Validation slug"""
        import re
        from django.utils.text import slugify
        import unicodedata

        slug = self.cleaned_data.get('slug', '').strip().lower()
        name = self.cleaned_data.get('name', '')

        if not slug and name:
            normalized = unicodedata.normalize('NFKD', name)
            cleaned = ''.join(c for c in normalized if not unicodedata.combining(c))
            cleaned = re.sub(r'[&/]', '-', cleaned)
            slug = slugify(cleaned)

        if slug:
            if len(slug) < 5:
                raise forms.ValidationError('Slug phải có ít nhất 5 ký tự.')

            if len(slug) > 120:
                raise forms.ValidationError('Slug không được quá 120 ký tự.')

            if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', slug):
                raise forms.ValidationError(
                    'Slug chỉ được chứa chữ thường, số và dấu gạch ngang. Không được bắt đầu/kết thúc bằng dấu gạch ngang.')

            existing = Product.objects.filter(slug=slug)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError('Slug này đã tồn tại. Vui lòng chọn slug khác.')

        return slug

    def clean_sku(self):
        """Validation SKU"""
        import re
        import time
        import random

        sku = self.cleaned_data.get('sku', '').strip().upper()
        sku = sku.replace(' ', '')

        if not sku:
            timestamp = int(time.time()) % 100000
            random_part = random.randint(100, 999)
            sku = f"SKU-{timestamp}-{random_part}"

        if len(sku) < 3:
            raise forms.ValidationError('Mã SKU phải có ít nhất 3 ký tự.')

        if len(sku) > 50:
            raise forms.ValidationError('Mã SKU không được quá 50 ký tự.')

        if not re.match(r'^[A-Z0-9_\-]+$', sku):
            raise forms.ValidationError('Mã SKU chỉ được chứa chữ cái, số, dấu gạch ngang và dấu gạch dưới.')

        existing = Product.objects.filter(sku__iexact=sku)
        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise forms.ValidationError('Mã SKU này đã tồn tại trong hệ thống.')

        return sku

    def clean_description(self):
        """Validation mô tả"""
        import re
        import html

        description = self.cleaned_data.get('description', '').strip()

        if not description:
            raise forms.ValidationError('Mô tả sản phẩm không được để trống.')

        plain_text = re.sub(r'<[^>]+>', '', description)
        plain_text = html.unescape(plain_text).strip()

        if len(plain_text) < 20:
            raise forms.ValidationError('Mô tả sản phẩm phải có ít nhất 20 ký tự (không tính thẻ HTML).')

        if len(description) > 5000:
            raise forms.ValidationError('Mô tả sản phẩm không được quá 5000 ký tự.')

        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'<iframe[^>]*>.*?</iframe>',
            r'<object[^>]*>.*?</object>',
            r'<embed[^>]*>',
            r'on\w+\s*=',
            r'javascript:',
        ]

        for pattern in dangerous_patterns:
            description = re.sub(pattern, '', description, flags=re.IGNORECASE | re.DOTALL)

        return description

    def clean_category(self):
        """Validation danh mục"""
        category = self.cleaned_data.get('category')

        if category and not category.is_active:
            raise forms.ValidationError('Danh mục này đã bị vô hiệu hóa. Vui lòng chọn danh mục khác.')

        return category

    def clean_brand(self):
        """Validation thương hiệu"""
        brand = self.cleaned_data.get('brand')

        if brand and not brand.is_active:
            raise forms.ValidationError('Thương hiệu này đã bị vô hiệu hóa. Vui lòng chọn thương hiệu khác.')

        return brand

    def clean_price(self):
        """Validation giá gốc"""
        from decimal import Decimal
        price = self.cleaned_data.get('price')

        if price is None:
            raise forms.ValidationError('Giá gốc không được để trống.')

        if price < 1000:
            raise forms.ValidationError('Giá gốc phải từ 1,000 VNĐ trở lên.')

        if price > 999999999999:
            raise forms.ValidationError('Giá gốc không được vượt quá 999,999,999,999 VNĐ.')

        if price != int(price):
            raise forms.ValidationError('Giá gốc phải là số nguyên (VNĐ không có xu).')

        return Decimal(int(price))

    def clean_sale_price(self):
        """Validation giá khuyến mãi"""
        from decimal import Decimal
        sale_price = self.cleaned_data.get('sale_price')

        if sale_price is None or sale_price == 0:
            return None

        if sale_price < 1000:
            raise forms.ValidationError('Giá khuyến mãi phải từ 1,000 VNĐ trở lên hoặc để trống.')

        if sale_price != int(sale_price):
            raise forms.ValidationError('Giá khuyến mãi phải là số nguyên.')

        return Decimal(int(sale_price))

    def clean_stock(self):
        """Validation tồn kho"""
        stock = self.cleaned_data.get('stock')

        if stock is None:
            stock = 0

        if stock < 0:
            raise forms.ValidationError('Số lượng tồn kho không được âm.')

        if stock > 999999:
            raise forms.ValidationError('Số lượng tồn kho không được vượt quá 999,999.')

        return stock

    def clean_image(self):
        """Validation hình ảnh"""
        image = self.cleaned_data.get('image')

        if image and hasattr(image, 'size'):
            if image.size > self.MAX_IMAGE_SIZE:
                raise forms.ValidationError(
                    f'Kích thước hình ảnh tối đa là 5MB. File hiện tại: {image.size / 1024 / 1024:.1f}MB')

            if hasattr(image, 'content_type'):
                if image.content_type not in self.ALLOWED_IMAGE_TYPES:
                    raise forms.ValidationError('Định dạng hình ảnh không hợp lệ. Chỉ chấp nhận: JPG, PNG, WebP.')
            else:
                import os
                ext = os.path.splitext(image.name)[1].lower()
                if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
                    raise forms.ValidationError('Định dạng hình ảnh không hợp lệ. Chỉ chấp nhận: JPG, PNG, WebP.')
        elif not self.instance.pk:
            pass

        return image

    def clean_specifications(self):
        """Validation thông số kỹ thuật"""
        import json
        specifications = self.cleaned_data.get('specifications')

        if specifications:
            if isinstance(specifications, str):
                try:
                    specifications = json.loads(specifications)
                except json.JSONDecodeError:
                    raise forms.ValidationError(
                        'Thông số kỹ thuật phải là JSON hợp lệ. VD: {"RAM": "8GB", "Storage": "256GB"}')

        return specifications

    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        sale_price = cleaned_data.get('sale_price')
        stock = cleaned_data.get('stock', 0)
        is_active = cleaned_data.get('is_active')
        is_featured = cleaned_data.get('is_featured')
        image = cleaned_data.get('image')

        if sale_price and price:
            if sale_price >= price:
                self.add_error('sale_price', 'Giá khuyến mãi phải nhỏ hơn giá gốc.')
            else:
                discount_percent = ((price - sale_price) / price) * 100
                if discount_percent > 70:
                    self.add_error('sale_price',
                                   f'Cảnh báo: Giảm giá {discount_percent:.0f}% (>70%). Vui lòng kiểm tra lại.')

        if stock == 0 and is_active:
            self.add_error('is_active', 'Cảnh báo: Tồn kho = 0, sản phẩm sẽ hiển thị "Hết hàng" trên website.')

        if is_featured and not self.instance.pk:
            featured_count = Product.objects.filter(is_featured=True).count()
            if featured_count >= self.MAX_FEATURED_PRODUCTS:
                self.add_error('is_featured',
                               f'Đã đạt giới hạn {self.MAX_FEATURED_PRODUCTS} sản phẩm nổi bật. Vui lòng bỏ nổi bật sản phẩm khác trước.')

        if not image and not self.instance.pk:
            if not hasattr(self, '_image_warning_shown'):
                self._image_warning_shown = True

        return cleaned_data


class CategoryForm(forms.ModelForm):
    """Form tạo/sửa danh mục với validation đầy đủ"""

    ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/svg+xml']
    MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2MB

    class Meta:
        model = Category
        fields = ['name', 'slug', 'description', 'image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: Điện thoại, Laptop Gaming'}),
            'slug': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'VD: dien-thoai (tự động tạo nếu để trống)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'maxlength': '1000'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': '.jpg,.jpeg,.png,.webp,.svg'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_name(self):
        """Validation tên danh mục"""
        import re
        name = self.cleaned_data.get('name', '').strip()

        if not name:
            raise forms.ValidationError('Tên danh mục không được để trống.')

        if len(name) < 2:
            raise forms.ValidationError('Tên danh mục phải có ít nhất 2 ký tự.')

        if len(name) > 100:
            raise forms.ValidationError('Tên danh mục không được quá 100 ký tự.')

        if not re.match(r'^[\w\s\-\u00C0-\u1EF9]+$', name, re.UNICODE):
            raise forms.ValidationError('Tên danh mục chỉ được chứa chữ cái, số, khoảng trắng và dấu gạch ngang.')

        existing = Category.objects.filter(name__iexact=name)
        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise forms.ValidationError('Tên danh mục này đã tồn tại.')

        return name

    def clean_slug(self):
        """Validation slug"""
        import re
        from django.utils.text import slugify

        slug = self.cleaned_data.get('slug', '').strip().lower()
        name = self.cleaned_data.get('name', '')

        if not slug and name:
            slug = slugify(name)

        if slug:
            if len(slug) < 2:
                raise forms.ValidationError('Slug phải có ít nhất 2 ký tự.')

            if len(slug) > 96:
                raise forms.ValidationError('Slug không được quá 96 ký tự.')

            if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', slug):
                raise forms.ValidationError(
                    'Slug chỉ được chứa chữ thường, số và dấu gạch ngang. Không được bắt đầu/kết thúc bằng dấu gạch ngang.')

            existing = Category.objects.filter(slug=slug)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError('Slug này đã tồn tại.')

        return slug

    def clean_description(self):
        """Validation mô tả"""
        import html
        description = self.cleaned_data.get('description', '').strip()

        if description and len(description) > 1000:
            raise forms.ValidationError('Mô tả không được quá 1000 ký tự.')

        if description:
            description = html.escape(description)

        return description

    def clean_image(self):
        """Validation hình ảnh"""
        image = self.cleaned_data.get('image')

        if image and hasattr(image, 'size'):
            if image.size > self.MAX_IMAGE_SIZE:
                raise forms.ValidationError(
                    f'Kích thước hình ảnh tối đa là 2MB. File hiện tại: {image.size / 1024 / 1024:.1f}MB')

            if hasattr(image, 'content_type'):
                if image.content_type not in self.ALLOWED_IMAGE_TYPES:
                    raise forms.ValidationError('Định dạng hình ảnh không hợp lệ. Chỉ chấp nhận: JPG, PNG, WebP, SVG.')
            else:
                import os
                ext = os.path.splitext(image.name)[1].lower()
                if ext not in ['.jpg', '.jpeg', '.png', '.webp', '.svg']:
                    raise forms.ValidationError('Định dạng hình ảnh không hợp lệ. Chỉ chấp nhận: JPG, PNG, WebP, SVG.')

        return image

    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()
        is_active = cleaned_data.get('is_active')

        if self.instance.pk and not is_active:
            product_count = self.instance.product_set.filter(is_active=True).count()
            if product_count > 0:
                self.add_error('is_active',
                               f'Cảnh báo: Danh mục này có {product_count} sản phẩm đang hoạt động. Tắt danh mục sẽ ẩn các sản phẩm này trên website.')

        return cleaned_data


class BrandForm(forms.ModelForm):
    """Form tạo/sửa thương hiệu với validation đầy đủ"""

    ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/svg+xml']
    MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2MB

    class Meta:
        model = Brand
        fields = ['name', 'slug', 'logo', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': "VD: Apple, Samsung, H&M, L'Oréal Paris"}),
            'slug': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'VD: apple, samsung (tự động tạo nếu để trống)'}),
            'logo': forms.FileInput(attrs={'class': 'form-control', 'accept': '.jpg,.jpeg,.png,.webp,.svg'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'maxlength': '1000'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_name(self):
        """Validation tên thương hiệu"""
        import re
        name = self.cleaned_data.get('name', '').strip()

        if not name:
            raise forms.ValidationError('Tên thương hiệu không được để trống.')

        if len(name) < 2:
            raise forms.ValidationError('Tên thương hiệu phải có ít nhất 2 ký tự.')

        if len(name) > 100:
            raise forms.ValidationError('Tên thương hiệu không được quá 100 ký tự.')

        if not re.match(r"^[\w\s\-&'.\u00C0-\u1EF9]+$", name, re.UNICODE):
            raise forms.ValidationError(
                "Tên thương hiệu chỉ được chứa chữ cái, số, khoảng trắng, dấu gạch ngang, & và dấu '.")

        existing = Brand.objects.filter(name__iexact=name)
        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise forms.ValidationError('Tên thương hiệu này đã tồn tại.')

        return name

    def clean_slug(self):
        """Validation slug"""
        import re
        from django.utils.text import slugify
        import unicodedata

        slug = self.cleaned_data.get('slug', '').strip().lower()
        name = self.cleaned_data.get('name', '')

        if not slug and name:
            normalized = unicodedata.normalize('NFKD', name)
            cleaned = ''.join(c for c in normalized if not unicodedata.combining(c))
            cleaned = re.sub(r"[&']", '', cleaned)
            slug = slugify(cleaned)

        if slug:
            if len(slug) < 2:
                raise forms.ValidationError('Slug phải có ít nhất 2 ký tự.')

            if len(slug) > 96:
                raise forms.ValidationError('Slug không được quá 96 ký tự.')

            if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', slug):
                raise forms.ValidationError(
                    'Slug chỉ được chứa chữ thường, số và dấu gạch ngang. Không được bắt đầu/kết thúc bằng dấu gạch ngang.')

            existing = Brand.objects.filter(slug=slug)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError('Slug này đã tồn tại.')

        return slug

    def clean_description(self):
        """Validation mô tả"""
        import html
        description = self.cleaned_data.get('description', '').strip()

        if description and len(description) > 1000:
            raise forms.ValidationError('Mô tả không được quá 1000 ký tự.')

        if description:
            description = html.escape(description)

        return description

    def clean_logo(self):
        """Validation logo"""
        logo = self.cleaned_data.get('logo')

        if logo and hasattr(logo, 'size'):
            if logo.size > self.MAX_IMAGE_SIZE:
                raise forms.ValidationError(
                    f'Kích thước logo tối đa là 2MB. File hiện tại: {logo.size / 1024 / 1024:.1f}MB')

            if hasattr(logo, 'content_type'):
                if logo.content_type not in self.ALLOWED_IMAGE_TYPES:
                    raise forms.ValidationError('Định dạng logo không hợp lệ. Chỉ chấp nhận: JPG, PNG, WebP, SVG.')
            else:
                import os
                ext = os.path.splitext(logo.name)[1].lower()
                if ext not in ['.jpg', '.jpeg', '.png', '.webp', '.svg']:
                    raise forms.ValidationError('Định dạng logo không hợp lệ. Chỉ chấp nhận: JPG, PNG, WebP, SVG.')

        return logo

    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()
        is_active = cleaned_data.get('is_active')

        if self.instance.pk and not is_active:
            product_count = self.instance.product_set.filter(is_active=True).count()
            if product_count > 0:
                self.add_error('is_active',
                               f'Cảnh báo: Thương hiệu này có {product_count} sản phẩm đang hoạt động. Tắt thương hiệu sẽ ẩn các sản phẩm này trên website.')

        return cleaned_data


class OrderStatusForm(forms.Form):
    """Form cập nhật trạng thái đơn hàng"""

    STATUS_CHOICES = Order.STATUS_CHOICES

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Ghi chú (tùy chọn)'})
    )


class UserEditForm(forms.ModelForm):
    """Form chỉnh sửa quyền user"""

    class Meta:
        model = User
        fields = ['is_active', 'is_staff', 'is_superuser']
        widgets = {
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class VoucherForm(forms.ModelForm):
    """Form tạo/sửa voucher với validation đầy đủ"""

    class Meta:
        model = Voucher
        fields = [
            'code', 'name', 'description', 'discount_type', 'discount_value',
            'min_order_value', 'max_discount', 'usage_limit', 'usage_limit_per_user',
            'valid_from', 'valid_until', 'is_active'
        ]
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: SALE2024'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: Giảm giá mùa hè'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'discount_type': forms.Select(attrs={'class': 'form-select'}),
            'discount_value': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'min_order_value': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '1000'}),
            'max_discount': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '1000'}),
            'usage_limit': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'usage_limit_per_user': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'valid_from': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'valid_until': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_code(self):
        """Validation mã voucher"""
        import re
        code = self.cleaned_data.get('code', '').strip()

        if not code:
            raise forms.ValidationError('Mã voucher không được để trống.')

        if len(code) < 4:
            raise forms.ValidationError('Mã voucher phải có ít nhất 4 ký tự.')

        if len(code) > 20:
            raise forms.ValidationError('Mã voucher không được quá 20 ký tự.')

        if not re.match(r'^[a-zA-Z0-9_]+$', code):
            raise forms.ValidationError('Mã voucher chỉ được chứa chữ cái, số và dấu gạch dưới (_).')

        existing = Voucher.objects.filter(code__iexact=code)
        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise forms.ValidationError('Mã voucher này đã tồn tại trong hệ thống.')

        return code.upper()

    def clean_name(self):
        """Validation tên voucher"""
        name = self.cleaned_data.get('name', '').strip()

        if not name:
            raise forms.ValidationError('Tên voucher không được để trống.')

        if len(name) < 5:
            raise forms.ValidationError('Tên voucher phải có ít nhất 5 ký tự.')

        if len(name) > 100:
            raise forms.ValidationError('Tên voucher không được quá 100 ký tự.')

        return name

    def clean_discount_value(self):
        """Validation giá trị giảm"""
        from decimal import Decimal
        discount_value = self.cleaned_data.get('discount_value')

        if discount_value is None or discount_value <= 0:
            raise forms.ValidationError('Giá trị giảm phải lớn hơn 0.')

        return discount_value

    def clean_max_discount(self):
        """Validation giảm tối đa"""
        max_discount = self.cleaned_data.get('max_discount')

        if max_discount is not None and max_discount < 0:
            raise forms.ValidationError('Giảm tối đa không được âm.')

        return max_discount

    def clean_min_order_value(self):
        """Validation đơn tối thiểu"""
        min_order_value = self.cleaned_data.get('min_order_value')

        if min_order_value is not None and min_order_value < 0:
            raise forms.ValidationError('Giá trị đơn tối thiểu không được âm.')

        return min_order_value

    def clean_usage_limit(self):
        """Validation giới hạn sử dụng"""
        usage_limit = self.cleaned_data.get('usage_limit')

        if usage_limit is not None and usage_limit < 0:
            raise forms.ValidationError('Giới hạn sử dụng không được âm.')

        return usage_limit

    def clean_usage_limit_per_user(self):
        """Validation giới hạn/người"""
        usage_limit_per_user = self.cleaned_data.get('usage_limit_per_user')

        if usage_limit_per_user is not None and usage_limit_per_user < 0:
            raise forms.ValidationError('Giới hạn/người không được âm.')

        return usage_limit_per_user

    def clean(self):
        """Cross-field validation"""
        from django.utils import timezone
        from decimal import Decimal

        cleaned_data = super().clean()
        discount_type = cleaned_data.get('discount_type')
        discount_value = cleaned_data.get('discount_value')
        max_discount = cleaned_data.get('max_discount')
        min_order_value = cleaned_data.get('min_order_value') or Decimal('0')
        usage_limit = cleaned_data.get('usage_limit') or 0
        usage_limit_per_user = cleaned_data.get('usage_limit_per_user') or 0
        valid_from = cleaned_data.get('valid_from')
        valid_until = cleaned_data.get('valid_until')

        if discount_type == 'percentage' and discount_value is not None:
            if discount_value <= 0 or discount_value > 100:
                self.add_error('discount_value', 'Phần trăm giảm phải từ 1 đến 100.')

            if not max_discount or max_discount <= 0:
                self.add_error('max_discount', 'Giảm tối đa là bắt buộc khi loại giảm giá là phần trăm.')

        if discount_type == 'fixed' and max_discount:
            cleaned_data['max_discount'] = None

        if max_discount and min_order_value:
            if max_discount >= min_order_value and min_order_value > 0:
                self.add_error('max_discount', 'Giảm tối đa phải nhỏ hơn giá trị đơn tối thiểu.')

        if usage_limit > 0 and usage_limit_per_user > 0:
            if usage_limit_per_user > usage_limit:
                self.add_error('usage_limit_per_user', 'Giới hạn/người không được lớn hơn giới hạn sử dụng tổng.')

        if valid_from and valid_until:
            if valid_until <= valid_from:
                self.add_error('valid_until', 'Ngày kết thúc phải sau ngày bắt đầu.')

            duration = valid_until - valid_from
            if duration.days > 365:
                self.add_error('valid_until', 'Thời hạn voucher không được quá 1 năm.')

            if duration.total_seconds() < 86400:
                self.add_error('valid_until', 'Thời hạn voucher phải ít nhất 1 ngày.')

        if not valid_from:
            self.add_error('valid_from', 'Ngày bắt đầu không được để trống.')

        if not valid_until:
            self.add_error('valid_until', 'Ngày kết thúc không được để trống.')

        return cleaned_data


class FlashSaleForm(forms.ModelForm):
    """Form tạo/sửa flash sale với validation đầy đủ"""

    class Meta:
        model = FlashSale
        fields = ['product', 'sale_price', 'quantity_limit', 'start_time', 'end_time', 'is_active']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'sale_price': forms.NumberInput(
                attrs={'class': 'form-control', 'min': '1000', 'step': '1000', 'placeholder': 'VD: 1500000'}),
            'quantity_limit': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'placeholder': 'VD: 50'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(is_active=True, stock__gt=0)
        self.fields['product'].empty_label = "-- Chọn sản phẩm --"

    def clean_product(self):
        """Validation sản phẩm"""
        product = self.cleaned_data.get('product')

        if not product:
            raise forms.ValidationError('Vui lòng chọn sản phẩm.')

        if not product.is_active:
            raise forms.ValidationError('Sản phẩm này không còn hoạt động.')

        if product.stock <= 0:
            raise forms.ValidationError('Sản phẩm này đã hết hàng.')

        return product

    def clean_sale_price(self):
        """Validation giá flash sale"""
        from decimal import Decimal
        sale_price = self.cleaned_data.get('sale_price')

        if sale_price is None:
            raise forms.ValidationError('Giá Flash Sale không được để trống.')

        if sale_price < 1000:
            raise forms.ValidationError('Giá Flash Sale phải từ 1,000 VNĐ trở lên.')

        if sale_price != int(sale_price):
            raise forms.ValidationError('Giá Flash Sale phải là số nguyên.')

        return Decimal(int(sale_price))

    def clean_quantity_limit(self):
        """Validation số lượng giới hạn"""
        quantity_limit = self.cleaned_data.get('quantity_limit')

        if quantity_limit is None or quantity_limit < 1:
            raise forms.ValidationError('Số lượng giới hạn phải ít nhất là 1.')

        return quantity_limit

    def clean_start_time(self):
        """Validation thời gian bắt đầu"""
        from django.utils import timezone
        start_time = self.cleaned_data.get('start_time')

        if not start_time:
            raise forms.ValidationError('Thời gian bắt đầu không được để trống.')

        return start_time

    def clean_end_time(self):
        """Validation thời gian kết thúc"""
        end_time = self.cleaned_data.get('end_time')

        if not end_time:
            raise forms.ValidationError('Thời gian kết thúc không được để trống.')

        return end_time

    def clean(self):
        """Cross-field validation"""
        from django.utils import timezone
        from django.db.models import Q

        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        sale_price = cleaned_data.get('sale_price')
        quantity_limit = cleaned_data.get('quantity_limit')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if product and sale_price:
            if sale_price >= product.price:
                self.add_error('sale_price', f'Giá Flash Sale phải nhỏ hơn giá gốc ({product.price:,.0f} VNĐ).')

            if product.sale_price and sale_price >= product.sale_price:
                self.add_error('sale_price',
                               f'Giá Flash Sale phải nhỏ hơn giá khuyến mãi hiện tại ({product.sale_price:,.0f} VNĐ).')

            if sale_price and product.price:
                discount_percent = ((product.price - sale_price) / product.price) * 100
                if discount_percent < 10:
                    self.add_error('sale_price',
                                   f'Cảnh báo: Giảm giá chỉ {discount_percent:.0f}% có thể không hấp dẫn.')
                elif discount_percent > 80:
                    self.add_error('sale_price',
                                   f'Cảnh báo: Giảm giá {discount_percent:.0f}% (>80%). Vui lòng kiểm tra lại.')

        if product and quantity_limit:
            if quantity_limit > product.stock:
                self.add_error('quantity_limit', f'Số lượng vượt quá tồn kho hiện tại ({product.stock}).')
            elif quantity_limit > product.stock * 0.8:
                self.add_error('quantity_limit', f'Cảnh báo: Đang dùng >80% tồn kho ({product.stock}) cho Flash Sale.')

        if start_time and end_time:
            if end_time <= start_time:
                self.add_error('end_time', 'Thời gian kết thúc phải sau thời gian bắt đầu.')
            else:
                duration_hours = (end_time - start_time).total_seconds() / 3600
                if duration_hours < 1:
                    self.add_error('end_time', 'Flash Sale phải diễn ra ít nhất 1 giờ.')
                elif duration_hours > 168:
                    self.add_error('end_time',
                                   f'Cảnh báo: Flash Sale quá dài ({duration_hours:.0f} giờ > 7 ngày). Hiệu quả có thể giảm.')

        if product and start_time and end_time:
            conflict_query = FlashSale.objects.filter(
                product=product
            ).filter(
                Q(start_time__lt=end_time, end_time__gt=start_time)
            )

            if self.instance.pk:
                conflict_query = conflict_query.exclude(pk=self.instance.pk)

            if conflict_query.exists():
                conflicting = conflict_query.first()
                self.add_error('product',
                               f'Sản phẩm này đã có Flash Sale từ {conflicting.start_time.strftime("%d/%m/%Y %H:%M")} đến {conflicting.end_time.strftime("%d/%m/%Y %H:%M")}.')

        return cleaned_data


class FlashSaleBatchForm(forms.Form):
    """Form tạo flash sale hàng loạt với validation đầy đủ"""

    discount_percent = forms.IntegerField(
        min_value=5,
        max_value=90,
        initial=20,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '5',
            'max': '90',
            'placeholder': 'VD: 20'
        })
    )

    quantity_limit = forms.IntegerField(
        min_value=1,
        max_value=999999,
        initial=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'placeholder': 'VD: 10'
        })
    )

    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )

    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )

    product_ids = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    def clean_discount_percent(self):
        """Validation phần trăm giảm giá"""
        discount_percent = self.cleaned_data.get('discount_percent')

        if discount_percent is None:
            raise forms.ValidationError('Phần trăm giảm giá không được để trống.')

        if discount_percent < 5:
            raise forms.ValidationError('Giảm giá tối thiểu 5%.')

        if discount_percent > 90:
            raise forms.ValidationError('Giảm giá tối đa 90%.')

        return discount_percent

    def clean_quantity_limit(self):
        """Validation số lượng mỗi sản phẩm"""
        quantity_limit = self.cleaned_data.get('quantity_limit')

        if quantity_limit is None or quantity_limit < 1:
            raise forms.ValidationError('Số lượng mỗi sản phẩm phải ít nhất là 1.')

        if quantity_limit > 999999:
            raise forms.ValidationError('Số lượng tối đa 999,999.')

        return quantity_limit

    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        discount_percent = cleaned_data.get('discount_percent')

        if not start_time:
            self.add_error('start_time', 'Thời gian bắt đầu không được để trống.')

        if not end_time:
            self.add_error('end_time', 'Thời gian kết thúc không được để trống.')

        if start_time and end_time:
            if end_time <= start_time:
                self.add_error('end_time', 'Thời gian kết thúc phải sau thời gian bắt đầu.')
            else:
                duration_hours = (end_time - start_time).total_seconds() / 3600
                if duration_hours < 1:
                    self.add_error('end_time', 'Flash Sale phải diễn ra ít nhất 1 giờ.')
                elif duration_hours > 168:
                    self.add_error('end_time', f'Cảnh báo: Flash Sale quá dài ({duration_hours:.0f} giờ > 7 ngày).')

        if discount_percent and discount_percent > 70:
            self.add_error('discount_percent', f'Cảnh báo: Giảm giá {discount_percent}% (>70%). Vui lòng kiểm tra kỹ.')

        return cleaned_data


class NotificationForm(forms.ModelForm):
    """Form tạo thông báo cho người dùng"""

    send_to = forms.ChoiceField(
        choices=[('all', 'Tất cả người dùng'), ('selected', 'Người dùng được chọn')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='all',
        label='Gửi đến'
    )

    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True).order_by('username'),
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': '8'}),
        required=False,
        label='Chọn người dùng'
    )

    class Meta:
        model = Notification
        fields = ['notification_type', 'title', 'message', 'url']
        widgets = {
            'notification_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'VD: Khuyến mãi đặc biệt',
                'maxlength': '200'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Nội dung thông báo...',
                'maxlength': '1000'
            }),
            'url': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'VD: /products/ hoặc để trống',
                'maxlength': '500'
            }),
        }

    def clean_notification_type(self):
        notification_type = self.cleaned_data.get('notification_type')
        if not notification_type:
            raise forms.ValidationError('Vui lòng chọn loại thông báo.')
        return notification_type

    def clean_title(self):
        import re
        title = self.cleaned_data.get('title', '').strip()

        if not title:
            raise forms.ValidationError('Tiêu đề không được để trống.')
        if len(title) < 5:
            raise forms.ValidationError('Tiêu đề phải có ít nhất 5 ký tự.')
        if len(title) > 200:
            raise forms.ValidationError('Tiêu đề không được quá 200 ký tự.')

        # Check for HTML tags
        if re.search(r'<[^>]*>', title):
            raise forms.ValidationError('Tiêu đề không được chứa HTML tags.')

        # Check for dangerous characters
        dangerous_chars = ['<', '>', '{', '}', '[', ']']
        if any(char in title for char in dangerous_chars):
            raise forms.ValidationError('Tiêu đề chứa ký tự không hợp lệ.')

        return title

    def clean_message(self):
        import re
        message = self.cleaned_data.get('message', '').strip()

        if not message:
            raise forms.ValidationError('Nội dung không được để trống.')
        if len(message) < 10:
            raise forms.ValidationError('Nội dung phải có ít nhất 10 ký tự.')
        if len(message) > 1000:
            raise forms.ValidationError('Nội dung không được quá 1000 ký tự.')

        # Check for dangerous HTML tags
        dangerous_tags = re.compile(r'<script|<iframe|<object|<embed|javascript:', re.IGNORECASE)
        if dangerous_tags.search(message):
            raise forms.ValidationError('Nội dung chứa thẻ không được phép.')

        return message

    def clean_url(self):
        import re
        url = self.cleaned_data.get('url', '').strip()

        if not url:
            return ''

        if len(url) > 500:
            raise forms.ValidationError('Đường dẫn quá dài (tối đa 500 ký tự).')

        # Check for XSS attempts
        xss_pattern = re.compile(r'javascript:|<script|<iframe|data:', re.IGNORECASE)
        if xss_pattern.search(url):
            raise forms.ValidationError('Đường dẫn chứa nội dung không hợp lệ.')

        # Validate URL format (relative path or absolute URL)
        valid_pattern = re.compile(r'^(\/[a-zA-Z0-9\-_\/\?&=%.#]*|https?:\/\/[^\s]+)$', re.IGNORECASE)
        if not valid_pattern.match(url):
            raise forms.ValidationError('Đường dẫn không hợp lệ. VD: /products hoặc https://example.com')

        return url

    def clean(self):
        cleaned_data = super().clean()
        send_to = cleaned_data.get('send_to')
        users = cleaned_data.get('users')

        if send_to == 'selected' and not users:
            self.add_error('users', 'Vui lòng chọn ít nhất một người dùng.')

        if send_to == 'selected' and users and len(users) > 5000:
            self.add_error('users', 'Chỉ được chọn tối đa 5000 người dùng mỗi lần gửi.')

        return cleaned_data
