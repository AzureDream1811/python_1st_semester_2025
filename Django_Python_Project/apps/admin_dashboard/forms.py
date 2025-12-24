"""
Forms cho Admin Dashboard
"""
from django import forms
from django.contrib.auth.models import User
from apps.products.models import Product, Category, Brand
from apps.orders.models import Order
from apps.promotions.models import Voucher, FlashSale


class ProductForm(forms.ModelForm):
    """Form tạo/sửa sản phẩm"""
    
    class Meta:
        model = Product
        fields = [
            'name', 'slug', 'sku', 'description', 'category', 'brand',
            'price', 'sale_price', 'stock', 'image', 'specifications',
            'is_active', 'is_featured', 'is_new'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'brand': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'specifications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_new': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CategoryForm(forms.ModelForm):
    """Form tạo/sửa danh mục"""
    
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description', 'image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class BrandForm(forms.ModelForm):
    """Form tạo/sửa thương hiệu"""
    
    class Meta:
        model = Brand
        fields = ['name', 'slug', 'logo', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }



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
    """Form tạo/sửa voucher"""
    
    class Meta:
        model = Voucher
        fields = [
            'code', 'name', 'description', 'discount_type', 'discount_value',
            'min_order_value', 'max_discount', 'usage_limit', 'usage_limit_per_user',
            'valid_from', 'valid_until', 'is_active'
        ]
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'discount_type': forms.Select(attrs={'class': 'form-select'}),
            'discount_value': forms.NumberInput(attrs={'class': 'form-control'}),
            'min_order_value': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_discount': forms.NumberInput(attrs={'class': 'form-control'}),
            'usage_limit': forms.NumberInput(attrs={'class': 'form-control'}),
            'usage_limit_per_user': forms.NumberInput(attrs={'class': 'form-control'}),
            'valid_from': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'valid_until': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class FlashSaleForm(forms.ModelForm):
    """Form tạo/sửa flash sale"""
    
    class Meta:
        model = FlashSale
        fields = ['product', 'sale_price', 'quantity_limit', 'start_time', 'end_time', 'is_active']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity_limit': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }