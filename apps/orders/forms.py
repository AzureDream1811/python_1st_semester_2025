from django import forms
from .models import Order


class CheckoutForm(forms.ModelForm):
    """Form thanh toán"""
    
    class Meta:
        model = Order
        fields = [
            'full_name', 'email', 'phone', 'address',
            'ward', 'district', 'city', 'note', 'payment_method'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Họ và tên người nhận'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Số điện thoại'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Địa chỉ chi tiết (số nhà, đường)'
            }),
            'ward': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phường/Xã'
            }),
            'district': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Quận/Huyện'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tỉnh/Thành phố'
            }),
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Ghi chú (không bắt buộc)',
                'rows': 3
            }),
            'payment_method': forms.RadioSelect(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Pre-fill thông tin từ user
        if user and user.is_authenticated:
            self.fields['full_name'].initial = user.get_full_name()
            self.fields['email'].initial = user.email
            self.fields['phone'].initial = user.phone
            
            # Lấy địa chỉ mặc định
            default_address = user.addresses.filter(is_default=True).first()
            if default_address:
                self.fields['full_name'].initial = default_address.full_name
                self.fields['phone'].initial = default_address.phone
                self.fields['address'].initial = default_address.address_line
                self.fields['ward'].initial = default_address.ward
                self.fields['district'].initial = default_address.district
                self.fields['city'].initial = default_address.city
